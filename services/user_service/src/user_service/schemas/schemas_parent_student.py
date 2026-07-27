from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


RelationshipType = Literal[
    "mother",
    "father",
    "guardian",
    "other",
]


class ParentStudentLinkCreate(BaseModel):
    """
    Создание связи родителя со студентом.
    """

    parent_id: int = Field(
        ...,
        gt=0,
        description="ID пользователя с ролью parent",
    )

    student_id: int = Field(
        ...,
        gt=0,
        description="ID пользователя с ролью student",
    )

    relationship: RelationshipType = Field(
        default="guardian",
        description="Тип родственной связи",
    )


class ParentStudentLinkUpdate(BaseModel):
    """
    Изменение типа родственной связи.
    """

    relationship: RelationshipType


class ParentStudentLinkResponse(BaseModel):
    """
    Ответ API с данными связи.
    """

    id: int
    parent_id: int
    student_id: int
    relationship: RelationshipType
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class LinkedUserResponse(BaseModel):
    """
    Краткие данные связанного пользователя.
    """

    id: int
    phone_number: str
    user_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class ParentStudentWithStudentResponse(
    ParentStudentLinkResponse
):
    """
    Связь вместе с профилем студента.
    """

    student: LinkedUserResponse


class ParentStudentWithParentResponse(
    ParentStudentLinkResponse
):
    """
    Связь вместе с профилем родителя.
    """

    parent: LinkedUserResponse