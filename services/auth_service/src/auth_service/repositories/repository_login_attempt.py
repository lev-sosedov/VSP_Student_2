import hashlib
from auth_service.models.models_login_attempt import LoginAttempt


class LoginAttemptRepository:
    def __init__(self, db):
        self.db = db

    async def record(self, *, phone: str, success: bool, reason_code: str,
                     ip_address: str | None, user_agent: str | None,
                     auth_user_id: int | None = None) -> None:
        self.db.add(LoginAttempt(
            phone_hash=hashlib.sha256(phone.strip().encode()).hexdigest(),
            success=success, reason_code=reason_code,
            ip_address=ip_address, user_agent=user_agent,
            auth_user_id=auth_user_id,
        ))
        await self.db.commit()
