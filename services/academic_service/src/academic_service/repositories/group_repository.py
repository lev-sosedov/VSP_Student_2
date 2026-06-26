from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from academic_service.models.group import Group


class GroupRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def create(self, group: Group):

        self.db.add(group)

        await self.db.commit()
        await self.db.refresh(group)

        return group


    async def get_by_id(self, group_id: int):

        result = await self.db.execute(
            select(Group)
            .where(Group.id == group_id)
        )

        return result.scalar_one_or_none()


    async def get_all(self):

        result = await self.db.execute(
            select(Group)
        )

        return result.scalars().all()