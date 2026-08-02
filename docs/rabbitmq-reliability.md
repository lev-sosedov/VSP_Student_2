# RabbitMQ reliability contract

All domain events use the versioned `common.messaging_contract.EventEnvelope`:
`event_id`, `event_type`, `event_version`, `occurred_at`, `producer`, optional
`correlation_id`/`causation_id`, and a bounded `payload`. RPC request/response
messages are separate contracts and are never sent to an event DLQ.

## Current topology

| Service | Role | Exchange | Queue / routing key | Durable | Ack / retry | DLQ | Idempotency | Outbox |
|---|---|---|---|---|---|---|---|---|
| auth-service | user event consumer | `user_security_events` (fanout) | `auth_user_sync` | yes, non-exclusive | after DB commit; 3 bounded retries | `auth_user_sync.v1.dlq` | `processed_user_events.event_id` | consumes user outbox |
| user-service | user event publisher/RPC server | `user_security_events` (fanout) | event routing key empty; `user_service.rpc` | yes | publisher confirm before `published_at` | n/a | outbox `event_id` unique | `user_event_outbox` |
| academic-service | event consumer/publisher/RPC server | `vsh_student` (topic) | `academic_service`, `academic.#` | yes | consumer commit then ACK | `academic_service.v1.dlq` | handler-specific | none (events are emitted after domain commit) |
| schedule-service | event publisher/RPC server | `vsh_student` (topic) | `schedule_service`, `schedule.#` | yes | persistent publisher confirms | n/a | n/a | none |
| content-service | event publisher/RPC client | `vsh_student` (topic) | `content.*` | yes | persistent publisher confirms | n/a | n/a | none |
| communication-service | event consumer/publisher/RPC client | `vsh_student` (topic) | `communication_service.academic_events` | yes, non-exclusive | commit then ACK; bounded retry | `communication_service.academic_events.v1.dlq` | domain event IDs | none |
| notification-service | event consumer/RPC client | `vsh_student` (topic) | `notification_service` | yes, non-exclusive | commit then ACK; bounded retry | `notification_service.v1.dlq` | `processed_events.event_id` | none |
| news-service | event publisher/RPC client | `vsh_student` (topic) | `news.*` | yes | persistent publisher confirms | n/a | n/a | none |

Existing queues are not re-declared with incompatible arguments. DLX/DLQ names
are versioned (`.v1`) so rollout does not require deleting or purging a live
queue. A future incompatible contract uses a new `.v2` queue and binding; the
old queue remains available for controlled drain/replay.

## Delivery and failure policy

Consumers parse and validate the envelope before applying business logic.
Malformed JSON and unsupported versions are published to the durable DLQ.
Transient failures use a bounded exponential retry (`1s`, `2s`, `4s`, capped)
and then go to the DLQ. A consumer exception never silently ACKs a message.
ACK is sent only after the business transaction commits. Duplicate deliveries
are successful no-ops using a unique `event_id` marker in the same transaction.

Outbox publishers select only unpublished, due rows, lock rows with
`SKIP LOCKED`, publish persistent messages with broker confirms, and set
`published_at` only after confirmation. Failures retain the row and update
retry metadata; no event is deleted. Payloads must not contain passwords,
JWTs, refresh tokens or private keys, and structured logs omit those fields.

## Readiness and operations

`/health` remains a cheap liveness endpoint. `/ready` checks required schema
tables and reports non-sensitive component readiness; it returns `503` until
the schema and required broker/RPC components are ready. Readiness responses
never include connection URLs, credentials or exception details.

Inspect a DLQ with RabbitMQ's read-only management/API tools. Do not purge or
delete messages during diagnosis. After fixing the cause, republish selected
messages to the original routing key with the original `event_id`; idempotency
prevents duplicate business changes.

## Safe rollout after merge

The code adds `user_service` revision `20260802_01` for outbox delivery
metadata (`retry_count`, `next_attempt_at`, `last_error_code`) and
`notification_service` revision `20260802_01` for durable `processed_events`.
Neither revision is applied automatically at startup.

1. Apply the new service migration in an isolated environment and verify one
   Alembic head.
2. In production, apply migrations one logical database at a time; do not
   stamp or upgrade the working database automatically.
3. Deploy consumers before publishers and verify `/ready`, queue durability,
   bindings and consumer counts.
4. Enable publishers, observe confirms/retries/DLQ, then remove legacy
   compatibility only after the queue is drained.
