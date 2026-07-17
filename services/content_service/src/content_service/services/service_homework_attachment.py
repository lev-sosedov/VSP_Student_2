from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_homework_attachment import (
    HomeworkAttachment
)
from content_service.repositories.repository_homework import (
    HomeworkRepository
)
from content_service.repositories.repository_homework_attachment import (
    HomeworkAttachmentRepository
)
from content_service.schemas.schemas_homework_attachment import (
    HomeworkAttachmentCreate,
    HomeworkAttachmentUpdate
)
from content_service.services.service_external_validation import (
    validate_content_author
)


class HomeworkAttachmentService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.attachment_repository = (
            HomeworkAttachmentRepository(
                session=session
            )
        )

        self.homework_repository = HomeworkRepository(
            session=session
        )

    # =================================================
    # Получить вложение по ID
    # =================================================

    async def get_by_id(
        self,
        attachment_id: int
    ) -> HomeworkAttachment | None:
        return await (
            self.attachment_repository.get_by_id(
                attachment_id=attachment_id
            )
        )

    # =================================================
    # Получить список вложений
    # =================================================

    async def get_list(
        self,
        homework_id: int | None = None,
        is_visible: bool | None = None,
        uploaded_by: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[HomeworkAttachment], int]:
        return await (
            self.attachment_repository.get_list(
                homework_id=homework_id,
                is_visible=is_visible,
                uploaded_by=uploaded_by,
                skip=skip,
                limit=limit
            )
        )

    # =================================================
    # Создать вложение
    # =================================================

    async def create(
        self,
        attachment_data: HomeworkAttachmentCreate
    ) -> HomeworkAttachment:
        homework = (
            await self.homework_repository.get_by_id(
                homework_id=attachment_data.homework_id
            )
        )

        if homework is None:
            raise ValueError(
                "Домашнее задание не найдено"
            )

        if not homework.is_active:
            raise ValueError(
                "Нельзя добавить вложение "
                "к неактивному домашнему заданию"
            )

        user = await validate_content_author(
            user_id=attachment_data.uploaded_by
        )

        if (
            user.get("role") in {
                "teacher",
                "TEACHER"
            }
            and homework.created_by
            != attachment_data.uploaded_by
        ):
            raise ValueError(
                "Преподаватель не является автором "
                "этого домашнего задания"
            )

        return await (
            self.attachment_repository.create(
                homework_id=attachment_data.homework_id,
                title=attachment_data.title,
                attachment_type=(
                    attachment_data.attachment_type
                ),
                file_url=attachment_data.file_url,
                file_name=attachment_data.file_name,
                mime_type=attachment_data.mime_type,
                file_size=attachment_data.file_size,
                sort_order=attachment_data.sort_order,
                is_visible=attachment_data.is_visible,
                uploaded_by=attachment_data.uploaded_by
            )
        )

    # =================================================
    # Изменить вложение
    # =================================================

    async def update(
        self,
        attachment: HomeworkAttachment,
        attachment_data: HomeworkAttachmentUpdate
    ) -> HomeworkAttachment:
        await self._validate_editor(
            attachment=attachment,
            user_id=attachment_data.updated_by
        )

        update_data = attachment_data.model_dump(
            exclude_unset=True,
            exclude={
                "updated_by"
            }
        )

        return await (
            self.attachment_repository.update(
                attachment=attachment,
                update_data=update_data
            )
        )

    # =================================================
    # Показать вложение
    # =================================================

    async def show(
        self,
        attachment: HomeworkAttachment,
        updated_by: int
    ) -> HomeworkAttachment:
        await self._validate_editor(
            attachment=attachment,
            user_id=updated_by
        )

        if attachment.is_visible:
            raise ValueError(
                "Вложение уже отображается студентам"
            )

        return await (
            self.attachment_repository.set_visibility(
                attachment=attachment,
                is_visible=True
            )
        )

    # =================================================
    # Скрыть вложение
    # =================================================

    async def hide(
        self,
        attachment: HomeworkAttachment,
        updated_by: int
    ) -> HomeworkAttachment:
        await self._validate_editor(
            attachment=attachment,
            user_id=updated_by
        )

        if not attachment.is_visible:
            raise ValueError(
                "Вложение уже скрыто"
            )

        return await (
            self.attachment_repository.set_visibility(
                attachment=attachment,
                is_visible=False
            )
        )

    # =================================================
    # Удалить вложение
    # =================================================

    async def delete(
        self,
        attachment: HomeworkAttachment,
        deleted_by: int
    ) -> None:
        await self._validate_editor(
            attachment=attachment,
            user_id=deleted_by
        )

        await self.attachment_repository.delete(
            attachment_id=attachment.id
        )

    # =================================================
    # Проверить пользователя
    # =================================================

    async def _validate_editor(
        self,
        attachment: HomeworkAttachment,
        user_id: int
    ) -> None:
        user = await validate_content_author(
            user_id=user_id
        )

        if (
            user.get("role") in {
                "teacher",
                "TEACHER"
            }
            and attachment.uploaded_by != user_id
        ):
            raise ValueError(
                "Преподаватель не загружал "
                "это вложение"
            )