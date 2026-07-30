import re

from pydantic import (
    BaseModel,
    Field,
    field_validator
)


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


class ContactMessageRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        ...,
        min_length=7,
        max_length=40
    )

    email: str = Field(
        ...,
        min_length=5,
        max_length=254
    )

    branch: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    message: str = Field(
        ...,
        min_length=5,
        max_length=5000
    )

    # Скрытое поле-ловушка для простых спам-ботов.
    website: str | None = Field(
        default=None,
        max_length=300
    )

    @field_validator(
        "name",
        "phone",
        "email",
        "branch",
        "message",
        "website"
    )
    @classmethod
    def strip_text(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        return value.strip()

    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        value: str
    ) -> str:
        normalized = value.lower()

        if not EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Укажите корректный email"
            )

        return normalized


class ContactMessageResponse(BaseModel):
    success: bool
    message: str
