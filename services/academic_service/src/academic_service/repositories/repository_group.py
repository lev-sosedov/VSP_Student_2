from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from academic_service.models.models_group import Group


class GroupRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    # Создание группы
    async def create(self,group: Group):
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)

        return group


    # Получить группу по id
    async def get_by_id(self,group_id: int):
        result = await self.db.execute(select(Group).where(Group.id == group_id))

        return result.scalar_one_or_none()


    # Все группы
    # async def get_all(self):
    #     result = await self.db.execute(select(Group).order_by(Group.id))
    #
    #     return result.scalars().all()

    # Все группы
    async def get_all(self,limit: int = 20,offset: int = 0):
        result = await self.db.execute(select(Group).order_by(Group.id).offset(offset).limit(limit))

        return result.scalars().all()


    # Активные группы
    async def get_active(self):
        result = await self.db.execute(select(Group).where(Group.is_active == True).order_by(Group.name))

        return result.scalars().all()


    # Закрытые группы
    async def get_closed(self):
        result = await self.db.execute(select(Group).where(Group.is_active == False))

        return result.scalars().all()


    # Группы филиала
    async def get_by_branch(self, branch_id: int):
        result = await self.db.execute(select(Group).where(Group.branch_id == branch_id))

        return result.scalars().all()


    # Группы направления
    async def get_by_direction(self,direction_id: int):
        result = await self.db.execute(select(Group).where(Group.direction_id == direction_id))

        return result.scalars().all()


    # Группы учебного плана
    async def get_by_plan(self, education_plan_id: int):
        result = await self.db.execute(select(Group).where(Group.education_plan_id ==education_plan_id))

        return result.scalars().all()


    # Поиск по названию
    async def search_by_name(self, name: str):
        result = await self.db.execute(select(Group).where(Group.name.ilike(f"%{name}%")))

        return result.scalars().all()


    # Проверка существования
    async def exists(self,group_id: int):
        result = await self.db.execute(select(Group.id).where(Group.id == group_id))

        return result.scalar_one_or_none() is not None


    # Проверка названия
    async def exists_by_name(self, name: str):
        result = await self.db.execute(select(Group.id).where(Group.name == name))

        return result.scalar_one_or_none() is not None


    # Обновление группы
    async def update(self, group_id: int, data: dict):
        await self.db.execute(update(Group).where(Group.id == group_id).values(**data))
        await self.db.commit()

        return await self.get_by_id(group_id)


    # Смена филиала
    async def update_branch(self, group_id: int, branch_id: int):
        await self.db.execute(update(Group).where(Group.id == group_id).values(branch_id=branch_id))
        await self.db.commit()

        return await self.get_by_id(group_id)


    # Смена направления
    async def update_direction(self, group_id: int, direction_id: int):
        await self.db.execute(update(Group).where(Group.id == group_id).values(direction_id=direction_id))
        await self.db.commit()

        return await self.get_by_id(group_id)


    # Смена учебного плана
    async def update_plan(self, group_id: int, education_plan_id: int):
        await self.db.execute(update(Group).where(Group.id == group_id).values(education_plan_id=education_plan_id))
        await self.db.commit()

        return await self.get_by_id(group_id)


    # Закрыть группу
    async def deactivate(self, group_id: int):
        group = await self.get_by_id(group_id)

        if group:
            group.is_active = False
            await self.db.commit()

        return group


    # Открыть группу
    async def activate(self, group_id: int):
        group = await self.get_by_id(group_id)

        if group:
            group.is_active = True
            await self.db.commit()

        return group


    # Количество участников
    async def count_members(self, group_id: int):
        result = await self.db.execute(select(func.count()).where(Group.id == group_id))

        return result.scalar()


    # Удаление группы
    async def delete(self, group_id: int):
        await self.db.execute(delete(Group).where(Group.id == group_id))

        await self.db.commit()

    # Получить группу по названию
    async def get_by_name(self, name: str):

        result = await self.db.execute(
            select(Group).where(
                Group.name == name
            )
        )

        return result.scalar_one_or_none()