from datetime import datetime
from typing import Any

from academic_service.clients.client_user_rpc import UserRpcClient
from academic_service.repositories.repository_group_member import GroupMemberRepository
from academic_service.repositories.repository_group import GroupRepository
from academic_service.models.models_group_member import GroupMember
from academic_service.schemas.schemas_group_member import (
    GroupMemberCreate,
    GroupMemberUpdate,
    GroupMemberPatch,
    GroupMemberLeave,
    GroupMemberActivate,
    GroupMemberTransfer
)

from common.utils.enum_role import RoleType


class GroupMemberService:

    def __init__(self, repo: GroupMemberRepository, group_repo: GroupRepository, user_client: UserRpcClient):
        self.repo = repo
        self.group_repo = group_repo
        self.user_client = user_client

    # добавить пользователя в группу
    async def add_member(self, data: GroupMemberCreate):
        group = await self.group_repo.get_by_id(data.group_id)

        if not group:
            raise ValueError("Group not found")

        if not group.is_active:
            raise ValueError("Group is closed")

        user = await self.user_client.get_user_by_id(data.user_id)

        if not user:
            raise ValueError("User not found")

        if not user["is_active"]:
            raise ValueError("User is inactive")

        if user["role"] != data.role:
            raise ValueError(f"User role is {user['role']}, "f"but group role is {data.role}")

        existing = await self.repo.get_by_group_user(data.group_id, data.user_id)

        if existing:
            if existing.is_active:
                raise ValueError("User already in group")

            member_id = int(existing.id)

            return await self.repo.update(member_id, {"role": data.role, "is_active": True, "left_at": None})

        member = GroupMember(group_id=data.group_id, user_id=data.user_id, role=data.role)

        return await self.repo.create(member)

    # получить участника
    async def get_member(self, member_id: int):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        return member

    # список преподавателей
    async def get_teachers(self, group_id: int):
        group = await self.group_repo.get_by_id(group_id)

        if not group:
            raise ValueError("Group not found")

        return await self.repo.get_teachers(group_id)

    # список участников группы
    async def get_group_members(self, group_id: int):

        return await self.repo.get_by_group(group_id)

    # список групп пользователя
    async def get_user_groups(self, user_id: int):

        return await self.repo.get_by_user(user_id)

    # изменить роль
    async def change_role(self, member_id: int, role: RoleType):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        role_value = (role.value if isinstance(role, RoleType) else role)

        return await self.repo.update(
            member_id, {"role": role_value})

    # назначить преподавателем
    async def assign_teacher(self, group_id: int, user_id: int):
        data = GroupMemberCreate(group_id=group_id, user_id=user_id, role="teacher")

        return await self.add_member(data)

    # назначить студента
    async def assign_student(self, group_id: int, user_id: int):
        data = GroupMemberCreate(group_id=group_id, user_id=user_id, role=RoleType.STUDENT)

        return await self.add_member(data)

    # убрать пользователя из группы
    async def remove_member(self, member_id: int):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        member_id = int(member.id)

        return await self.repo.update(
            member_id, {"is_active": False, "left_at": datetime.utcnow()})

    # восстановить участника
    async def restore_member(self, member_id: int):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        return await self.repo.update(
            member_id, {"is_active": True, "left_at": None})

    # полное обновление
    async def update_member(self, member_id: int, data: GroupMemberUpdate):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        update_data: dict[str, Any] = {}

        if data.group_id is not None:
            group = await self.group_repo.get_by_id(data.group_id)

            if not group:
                raise ValueError("Group not found")

            if not group.is_active:
                raise ValueError("Group is closed")

            update_data["group_id"] = data.group_id

        user = None

        if data.user_id is not None:
            user = await self.user_client.get_user_by_id(data.user_id)

            if not user:
                raise ValueError("User not found")

            if not user["is_active"]:
                raise ValueError("User is inactive")

            update_data["user_id"] = data.user_id

        if data.role is not None:
            role_value = (
                data.role.value
                if hasattr(data.role, "value")
                else str(data.role)).lower()

            checked_user = user

            if checked_user is None:
                checked_user = await self.user_client.get_user_by_id(
                    data.user_id
                    if data.user_id is not None
                    else member.user_id)

            if not checked_user:
                raise ValueError("User not found")

            user_role = (
                checked_user["role"].value
                if hasattr(checked_user["role"], "value")
                else str(checked_user["role"])).lower()

            if user_role != role_value:
                raise ValueError(f"User role is {user_role}, "f"but group role is {role_value}")

            update_data["role"] = role_value

        return await self.repo.update(member_id, update_data)

    # PATCH обновление
    async def patch_member(self, member_id: int, data: GroupMemberPatch):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        patch_data: dict[str, Any] = {}

        if data.role is not None:
            user = await self.user_client.get_user_by_id(member.user_id)

            if not user:
                raise ValueError("User not found")

            if not user["is_active"]:
                raise ValueError("User is inactive")

            user_role = (user["role"].value
                         if hasattr(user["role"], "value")
                         else str(user["role"])).lower()

            new_role = (data.role.value
                        if hasattr(data.role, "value")
                        else str(data.role)).lower()

            if user_role != new_role:
                raise ValueError(f"User role is {user_role}, "f"but group role is {new_role}")

            patch_data["role"] = new_role

        if data.is_active is not None:
            patch_data["is_active"] = data.is_active

            if data.is_active:
                patch_data["left_at"] = None
            else:
                patch_data["left_at"] = datetime.utcnow()

        return await self.repo.update(member_id, patch_data)

    # удалить полностью
    async def delete_member(self, member_id: int):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        return await self.repo.delete(member_id)

    # проверить участие
    async def is_member(self, group_id: int, user_id: int):
        member = await self.repo.get_by_group_user(group_id, user_id)

        return bool(member and member.is_active)

    # выход из группы
    async def leave_group(self, member_id: int, data: GroupMemberLeave):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        return await self.repo.update(
            member_id, {"is_active": False, "left_at": data.left_at})

    # активировать участника
    async def activate_member(self, member_id: int, data: GroupMemberActivate):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        update_data: dict[str, Any] = {"is_active": data.is_active}

        if data.is_active:
            update_data["left_at"] = None
        else:
            update_data["left_at"] = datetime.utcnow()

        return await self.repo.update(member_id, update_data)

    # перенос пользователя между группами
    async def transfer_member(self, data: GroupMemberTransfer):
        member = await self.repo.get_by_group_user(data.old_group_id, data.user_id)

        if not member:
            raise ValueError("Member not found")

        new_group = await self.group_repo.get_by_id(data.new_group_id)

        if not new_group:
            raise ValueError("New group not found")

        if not new_group.is_active:
            raise ValueError("New group is closed")

        duplicate = await self.repo.get_by_group_user(data.new_group_id, data.user_id)

        if duplicate and duplicate.is_active:
            raise ValueError("User already belongs to the new group")

        return await self.repo.update(
            member.id, {"group_id": data.new_group_id})

    # количество студентов
    async def count_students(self, group_id: int):
        return await self.repo.count_students(group_id)

    # количество преподавателей
    async def count_teachers(self, group_id: int):
        return await self.repo.count_teachers(group_id)

    # количество всех активных участников
    async def count_members(self, group_id: int):
        members = await self.repo.get_by_group(group_id)

        return len(members)
