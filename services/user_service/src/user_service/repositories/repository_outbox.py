import json
from datetime import datetime
from sqlalchemy import select, update
from user_service.models.model_outbox import UserEventOutbox


class OutboxRepository:
    def __init__(self, db):
        self.db = db

    async def add(self, *, event_id, event_type, user_id, auth_id=None, payload=None):
        event = UserEventOutbox(
            event_id=event_id,
            event_type=event_type,
            user_id=user_id,
            auth_id=auth_id,
            payload=json.dumps(payload or {}, separators=(",", ":"), sort_keys=True),
        )
        self.db.add(event)
        return event

    async def pending(self, limit=100):
        result = await self.db.execute(
            select(UserEventOutbox).where(UserEventOutbox.published_at.is_(None)).limit(limit)
        )
        return list(result.scalars().all())

    async def mark_published(self, event_id):
        await self.db.execute(
            update(UserEventOutbox).where(UserEventOutbox.event_id == event_id).values(published_at=datetime.utcnow())
        )
