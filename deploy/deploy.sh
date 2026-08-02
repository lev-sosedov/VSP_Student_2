#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env.production"
COMPOSE=(docker compose --env-file "${ENV_FILE}" -f "${ROOT_DIR}/docker-compose.prod.yml")
die() { printf 'deploy error: %s\n' "$1" >&2; exit 1; }
[[ -f "${ENV_FILE}" ]] || die "missing ${ENV_FILE}"
set -a
source "${ENV_FILE}"
set +a
[[ -r "${JWT_PRIVATE_KEY_HOST_PATH:-}" ]] || die "private RSA key is not readable"
[[ -r "${JWT_PUBLIC_KEY_HOST_PATH:-}" ]] || die "public RSA key is not readable"
[[ "${AUTO_CREATE_TABLES:-false}" == "false" ]] || die "AUTO_CREATE_TABLES must be false"
openssl rsa -in "${JWT_PRIVATE_KEY_HOST_PATH}" -check -noout >/dev/null 2>&1 || die "invalid private RSA key"
openssl rsa -pubin -in "${JWT_PUBLIC_KEY_HOST_PATH}" -noout >/dev/null 2>&1 || die "invalid public RSA key"
"${ROOT_DIR}/deploy/backup-postgres.sh"
"${COMPOSE[@]}" config --quiet
"${COMPOSE[@]}" build
for service in auth-service user-service academic-service schedule-service content-service communication-service notification-service news-service; do
  "${COMPOSE[@]}" run --rm "${service}" alembic upgrade head
done
"${COMPOSE[@]}" up -d
"${COMPOSE[@]}" ps
