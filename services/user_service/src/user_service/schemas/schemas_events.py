from pydantic import BaseModel


# создание пользователя (из auth_service)
class UserCreatedEvent(BaseModel):
    auth_id: int
    phone_number: str
    user_name: str | None = None