"""Role normalization shared by the identity producer and consumer."""

from common.identity.exceptions import UnknownRoleError
from common.utils.enum_role import RoleType


def normalize_role(value: RoleType | str) -> RoleType:
    if isinstance(value, RoleType):
        return value
    if not isinstance(value, str) or not value.strip():
        raise UnknownRoleError()

    normalized = value.strip().lower()
    for role in RoleType:
        if normalized in {role.value.lower(), role.name.lower()}:
            return role
    raise UnknownRoleError()
