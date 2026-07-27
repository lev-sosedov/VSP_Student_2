from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from user_service.models.model_parent_student import (
    ParentStudentLink,
)


class ParentStudentRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        link: ParentStudentLink,
    ) -> ParentStudentLink:
        self.db.add(link)

        await self.db.commit()
        await self.db.refresh(link)

        return link

    async def get_by_id(
        self,
        link_id: int,
    ) -> ParentStudentLink | None:
        result = await self.db.execute(
            select(ParentStudentLink)
            .options(
                selectinload(
                    ParentStudentLink.parent
                ),
                selectinload(
                    ParentStudentLink.student
                ),
            )
            .where(
                ParentStudentLink.id == link_id
            )
        )

        return result.scalar_one_or_none()

    async def get_existing(
        self,
        parent_id: int,
        student_id: int,
    ) -> ParentStudentLink | None:
        """
        Проверка существования связи между
        конкретным родителем и студентом.
        """

        result = await self.db.execute(
            select(ParentStudentLink)
            .where(
                ParentStudentLink.parent_id
                == parent_id,
                ParentStudentLink.student_id
                == student_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_parent(
        self,
        parent_id: int,
        active_only: bool = True,
    ) -> list[ParentStudentLink]:
        query = (
            select(ParentStudentLink)
            .options(
                selectinload(
                    ParentStudentLink.student
                )
            )
            .where(
                ParentStudentLink.parent_id
                == parent_id
            )
            .order_by(
                ParentStudentLink.created_at.desc()
            )
        )

        if active_only:
            query = query.where(
                ParentStudentLink.is_active
                .is_(True)
            )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    async def get_by_student(
        self,
        student_id: int,
        active_only: bool = True,
    ) -> list[ParentStudentLink]:
        query = (
            select(ParentStudentLink)
            .options(
                selectinload(
                    ParentStudentLink.parent
                )
            )
            .where(
                ParentStudentLink.student_id
                == student_id
            )
            .order_by(
                ParentStudentLink.created_at.desc()
            )
        )

        if active_only:
            query = query.where(
                ParentStudentLink.is_active
                .is_(True)
            )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    async def update_relationship(
        self,
        link: ParentStudentLink,
        relationship: str,
    ) -> ParentStudentLink:
        link.relationship = relationship

        self.db.add(link)

        await self.db.commit()
        await self.db.refresh(link)

        return link

    async def activate(
        self,
        link: ParentStudentLink,
    ) -> ParentStudentLink:
        link.is_active = True

        self.db.add(link)

        await self.db.commit()
        await self.db.refresh(link)

        return link

    async def deactivate(
        self,
        link: ParentStudentLink,
    ) -> ParentStudentLink:
        """
        Мягкое удаление связи.

        Запись остаётся в базе, но считается
        неактивной.
        """

        link.is_active = False

        self.db.add(link)

        await self.db.commit()
        await self.db.refresh(link)

        return link

    async def delete(
        self,
        link: ParentStudentLink,
    ) -> None:
        """
        Полное удаление связи.

        Пока основной API будет использовать
        мягкое удаление через deactivate().
        """

        await self.db.delete(link)
        await self.db.commit()