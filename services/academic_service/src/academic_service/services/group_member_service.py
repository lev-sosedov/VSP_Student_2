from academic_service.repositories.group_member_repository import GroupMemberRepository
from academic_service.repositories.group_repository import GroupRepository
from academic_service.schemas.group_member import (
    GroupMemberCreate,
    GroupMemberUpdate,
    GroupMemberPatch,
    GroupMemberFilter,
    GroupMemberLeave,
    GroupMemberActivate,
    GroupMemberTransfer,
    GroupMemberBulkCreate
)

from common.utils.enum_role import RoleType


class GroupMemberService:

    def __init__(self,repo: GroupMemberRepository,group_repo: GroupRepository):
        self.repo = repo
        self.group_repo = group_repo


    # добавить пользователя в группу
    async def add_member(self,data: GroupMemberCreate):
        group = await self.group_repo.get_by_id(data.group_id)

        if not group:
            raise ValueError("Group not found")

        if not group.is_active:
            raise ValueError("Group is closed")

        existing = await self.repo.get_by_group_user(data.group_id,data.user_id)

        if existing:
            if existing.is_active:
                raise ValueError("User already in group")

            existing.is_active = True
            existing.left_at = None

            return await self.repo.update(existing)

        member = await self.repo.create(data)

        return member


    # получить участника
    async def get_member(self,member_id:int):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        return member




    # список участников группы
    async def get_group_members(self,group_id:int):

        return await self.repo.get_by_group(group_id)


    # список групп пользователя
    async def get_user_groups(self,user_id:int):

        return await self.repo.get_by_user(user_id)


    # изменить роль
    async def change_role(self,member_id:int,role:RoleType):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        member.role = role

        return await self.repo.update(member)


    # назначить преподавателем
    async def assign_teacher(self,group_id:int,user_id:int):
        teacher = await self.repo.get_teacher(group_id)

        if teacher:
            raise ValueError("Teacher already assigned")

        data = GroupMemberCreate(group_id=group_id,user_id=user_id,role=RoleType.TEACHER)

        return await self.add_member(data)


    # назначить студента
    async def assign_student(self,group_id:int,user_id:int):
        data = GroupMemberCreate(group_id=group_id,user_id=user_id,role=RoleType.STUDENT)

        return await self.add_member(data)


    # убрать пользователя из группы
    async def remove_member(self,member_id:int):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        member.is_active = False

        return await self.repo.update(member)


    # восстановить участника
    async def restore_member(self,member_id:int):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        member.is_active = True
        member.left_at = None

        return await self.repo.update(member)


    # полное обновление
    async def update_member(self,member_id:int,data:GroupMemberUpdate):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        if data.group_id is not None:
            member.group_id = data.group_id

        if data.user_id is not None:
            member.user_id = data.user_id

        if data.role is not None:
            member.role = data.role

        return await self.repo.update(member)


    # PATCH обновление
    async def patch_member(self,member_id:int,data:GroupMemberPatch):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        if data.role is not None:
            member.role = data.role

        if data.is_active is not None:
            member.is_active = data.is_active
            if data.is_active:
                member.left_at = None

        return await self.repo.update(member)


    # удалить полностью
    async def delete_member(self, member_id:int):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        return await self.repo.delete(member_id)


    # проверить участие
    async def is_member(self,group_id:int,user_id:int):
        member = await self.repo.get_by_group_user(group_id,user_id)

        return bool(member and member.is_active)


    # фильтрация участников
    async def filter_members(self,filters:GroupMemberFilter):

        return await self.repo.filter(
            group_id=filters.group_id,
            user_id=filters.user_id,
            role=filters.role,
            is_active=filters.is_active)


    # выход из группы
    async def leave_group(self,member_id:int,data:GroupMemberLeave):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        member.is_active = False
        member.left_at = data.left_at

        return await self.repo.update(member)


    # активировать участника
    async def activate_member(self,member_id:int,data:GroupMemberActivate):
        member = await self.repo.get_by_id(member_id)

        if not member:
            raise ValueError("Member not found")

        member.is_active = data.is_active

        if data.is_active:
            member.left_at = None

        return await self.repo.update(member)


    # получить преподавателя группы
    async def get_teacher(self,group_id:int):

        return await self.repo.get_teacher(group_id)


    # перенос пользователя между группами
    async def transfer_member(self,data:GroupMemberTransfer):
        member = await self.repo.get_by_group_user(data.old_group_id,data.user_id)

        if not member:
            raise ValueError("Member not found")

        member.group_id = data.new_group_id

        return await self.repo.update(member)


    # массовое добавление
    async def bulk_create(self,data:GroupMemberBulkCreate):
        result = []
        for member_data in data.members:
            member = await self.add_member(member_data)
            result.append(member)

        return result


    # количество студентов
    async def count_students(self,group_id:int):
        members = await self.repo.get_by_group(group_id)

        return len([ m for m in members if m.role == RoleType.STUDENT and m.is_active ])


    # количество преподавателей
    async def count_teachers(self,group_id:int):
        members = await self.repo.get_by_group(group_id)

        return len([ m for m in members if m.role == RoleType.TEACHER and m.is_active ])


    # количество всех участников
    async def count_members(self,group_id:int):
        members = await self.repo.get_by_group(group_id)

        return len([ m for m in members if m.is_active ])