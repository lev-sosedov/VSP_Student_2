from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from academic_service.models.models_group_member import GroupMember


class GroupMemberRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Добавить участника в группу
    async def create(self, member: GroupMember):
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)

        return member

    # Получить по id
    async def get_by_id(self, member_id: int):
        result = await self.db.execute(select(GroupMember).where(GroupMember.id == member_id))

        return result.scalar_one_or_none()

    # Все участники
    async def get_all(self):
        result = await self.db.execute(select(GroupMember).order_by(GroupMember.id))

        return result.scalars().all()

    # Все участники группы
    async def get_by_group(self, group_id: int):
        result = await self.db.execute(select(GroupMember)
                                       .where(GroupMember.group_id == group_id)
                                       .where(GroupMember.is_active == True))

        return result.scalars().all()

    # Только студенты группы
    async def get_students(self, group_id: int):
        result = await self.db.execute(select(GroupMember)
                                       .where(GroupMember.group_id == group_id)
                                       .where(GroupMember.role == "student")
                                       .where(GroupMember.is_active == True))

        return result.scalars().all()

    # Только преподаватели группы
    async def get_teachers(self, group_id: int):

        result = await self.db.execute(select(GroupMember)
                                       .where(GroupMember.group_id == group_id)
                                       .where(GroupMember.role == "teacher")
                                       .where(GroupMember.is_active == True))

        return result.scalars().all()

    # Все группы пользователя
    async def get_by_user(self, user_id: int):
        result = await self.db.execute(select(GroupMember)
                                       .where(GroupMember.user_id == user_id)
                                       .where(GroupMember.is_active == True))

        return result.scalars().all()

    # Проверка состоит ли пользователь в группе
    async def exists(self, group_id: int, user_id: int):
        result = await self.db.execute(select(GroupMember.id)
                                       .where(GroupMember.group_id == group_id,
                                              GroupMember.user_id == user_id,
                                              GroupMember.is_active == True))

        return result.scalar_one_or_none() is not None

    # Получить конкретного пользователя в группе
    async def get_by_group_user(self, group_id: int, user_id: int):
        result = await self.db.execute(
            select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id))

        return result.scalar_one_or_none()

    # Изменить роль
    async def update_role(self, member_id: int, role: str):
        await self.db.execute(update(GroupMember).where(GroupMember.id == member_id).values(role=role))
        await self.db.commit()

        return await self.get_by_id(member_id)

    # Перевести в другую группу
    async def move_to_group(self, member_id: int, new_group_id: int):
        await self.db.execute(update(GroupMember).where(GroupMember.id == member_id).values(group_id=new_group_id))
        await self.db.commit()

        return await self.get_by_id(member_id)

    # Обновление данных
    async def update(self, member_id: int, data: dict):
        await self.db.execute(update(GroupMember).where(GroupMember.id == member_id).values(**data))
        await self.db.commit()

        return await self.get_by_id(member_id)

    # Участник покинул группу
    async def deactivate(self, member_id: int):
        member = await self.get_by_id(member_id)

        if member:
            member.is_active = False
            await self.db.commit()

        return member

    # Вернуть в группу
    async def activate(self, member_id: int):
        member = await self.get_by_id(member_id)

        if member:
            member.is_active = True
            await self.db.commit()

        return member

    # Количество студентов
    async def count_students(self, group_id: int):
        result = await self.db.execute(select(func.count())
                                       .where(GroupMember.group_id == group_id)
                                       .where(GroupMember.role == "student")
                                       .where(GroupMember.is_active == True))

        return result.scalar()

    # Количество преподавателей
    async def count_teachers(self, group_id: int):
        result = await self.db.execute(select(func.count())
                                       .where(GroupMember.group_id == group_id)
                                       .where(GroupMember.role == "teacher")
                                       .where(GroupMember.is_active == True))

        return result.scalar()

    # Удаление записи
    async def delete(self, member_id: int):
        await self.db.execute(delete(GroupMember).where(GroupMember.id == member_id))

        await self.db.commit()

    # получить преподавателя группы
    async def get_teacher(self, group_id: int):
        result = await self.db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.role == "teacher",
                GroupMember.is_active == True
            )
        )

        return result.scalar_one_or_none()
