from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_role import RoleType

from user_service.models.model_parent_student import (
    ParentStudentLink,
)
from user_service.repositories.repository_parent_student import (
    ParentStudentRepository,
)
from user_service.repositories.repository_user import (
    UserRepository,
)


class ParentStudentService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.parent_student_repo = (
            ParentStudentRepository(db)
        )
        self.user_repo = UserRepository(db)

    async def create_link(
        self,
        parent_id: int,
        student_id: int,
        relationship: str,
    ) -> ParentStudentLink:
        """
        Создать связь родителя со студентом.

        Если такая связь раньше была отключена,
        она восстанавливается.
        """

        if parent_id == student_id:
            raise ValueError(
                "Родитель и студент не могут быть "
                "одним пользователем"
            )

        parent = await self.user_repo.get_by_id(
            parent_id
        )

        if not parent:
            raise ValueError(
                "Родитель не найден"
            )

        student = await self.user_repo.get_by_id(
            student_id
        )

        if not student:
            raise ValueError(
                "Студент не найден"
            )

        if parent.role != RoleType.PARENT:
            raise ValueError(
                "Выбранный пользователь не имеет "
                "роль parent"
            )

        if student.role != RoleType.STUDENT:
            raise ValueError(
                "Выбранный пользователь не имеет "
                "роль student"
            )

        existing_link = (
            await self.parent_student_repo
            .get_existing(
                parent_id=parent_id,
                student_id=student_id,
            )
        )

        if existing_link:
            if existing_link.is_active:
                raise ValueError(
                    "Этот студент уже привязан "
                    "к родителю"
                )

            existing_link.relationship = (
                relationship
            )

            return (
                await self.parent_student_repo
                .activate(existing_link)
            )

        link = ParentStudentLink(
            parent_id=parent_id,
            student_id=student_id,
            relationship=relationship,
            is_active=True,
        )

        return (
            await self.parent_student_repo
            .create(link)
        )

    async def get_link(
        self,
        link_id: int,
    ) -> ParentStudentLink:
        link = (
            await self.parent_student_repo
            .get_by_id(link_id)
        )

        if not link:
            raise ValueError(
                "Связь родителя и студента "
                "не найдена"
            )

        return link

    async def get_parent_children(
        self,
        parent_id: int,
        active_only: bool = True,
    ) -> list[ParentStudentLink]:
        """
        Получить детей выбранного родителя.
        """

        parent = await self.user_repo.get_by_id(
            parent_id
        )

        if not parent:
            raise ValueError(
                "Родитель не найден"
            )

        if parent.role != RoleType.PARENT:
            raise ValueError(
                "Пользователь не имеет роль parent"
            )

        return (
            await self.parent_student_repo
            .get_by_parent(
                parent_id=parent_id,
                active_only=active_only,
            )
        )

    async def get_student_parents(
        self,
        student_id: int,
        active_only: bool = True,
    ) -> list[ParentStudentLink]:
        """
        Получить родителей выбранного студента.
        """

        student = await self.user_repo.get_by_id(
            student_id
        )

        if not student:
            raise ValueError(
                "Студент не найден"
            )

        if student.role != RoleType.STUDENT:
            raise ValueError(
                "Пользователь не имеет роль student"
            )

        return (
            await self.parent_student_repo
            .get_by_student(
                student_id=student_id,
                active_only=active_only,
            )
        )

    async def update_relationship(
        self,
        link_id: int,
        relationship: str,
    ) -> ParentStudentLink:
        """
        Изменить тип связи:
        mother, father, guardian или other.
        """

        link = await self.get_link(link_id)

        return (
            await self.parent_student_repo
            .update_relationship(
                link=link,
                relationship=relationship,
            )
        )

    async def deactivate_link(
        self,
        link_id: int,
    ) -> ParentStudentLink:
        """
        Отключить связь без физического удаления.
        """

        link = await self.get_link(link_id)

        if not link.is_active:
            raise ValueError(
                "Связь уже отключена"
            )

        return (
            await self.parent_student_repo
            .deactivate(link)
        )

    async def activate_link(
        self,
        link_id: int,
    ) -> ParentStudentLink:
        """
        Восстановить ранее отключённую связь.
        """

        link = await self.get_link(link_id)

        if link.is_active:
            raise ValueError(
                "Связь уже активна"
            )

        parent = await self.user_repo.get_by_id(
            link.parent_id
        )
        student = await self.user_repo.get_by_id(
            link.student_id
        )

        if not parent or (
            parent.role != RoleType.PARENT
        ):
            raise ValueError(
                "Родитель не найден или его роль "
                "была изменена"
            )

        if not student or (
            student.role != RoleType.STUDENT
        ):
            raise ValueError(
                "Студент не найден или его роль "
                "была изменена"
            )

        return (
            await self.parent_student_repo
            .activate(link)
        )