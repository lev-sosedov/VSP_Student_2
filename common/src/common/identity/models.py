"""Validated DTOs used by the identity-resolution RPC contract."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from common.identity.roles import normalize_role
from common.utils.enum_role import RoleType


class UserIdentityProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: int = Field(strict=True, gt=0)
    auth_user_id: int = Field(strict=True, gt=0)
    role: RoleType
    is_active: bool = Field(strict=True)
    is_account_verified: bool | None = Field(strict=True)

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: object) -> RoleType:
        return normalize_role(value)  # type: ignore[arg-type]


class ResolvedIdentity(UserIdentityProfile):
    token_version: int = Field(strict=True, ge=1)
