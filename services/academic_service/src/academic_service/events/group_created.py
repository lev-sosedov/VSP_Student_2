from pydantic import BaseModel


class GroupCreatedEvent(BaseModel):

    event: str = "group_created"

    group_id: int
    name: str
    direction_id: int