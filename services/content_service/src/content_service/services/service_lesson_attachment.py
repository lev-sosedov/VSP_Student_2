from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_lesson_attachment import (
    LessonAttachment
)
from content_service.repositories.repository_lesson_attachment import (
    LessonAttachmentRepository
)
from content_service.repositories.repository_lesson_content import (
    LessonContentRepository
)
from content_service.schemas.schemas_lesson_attachment import (
    LessonAttachmentCreate,
    LessonAttachmentUpdate
)
from content_service.services.service_external_validation import (
    validate_content_author
)


class LessonAttachmentService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.attachment_repository = (
            LessonAttachmentRepository(
                session=session
            )
        )

        self.content_repository = LessonContentRepository(
            session=session
        )

    # =================================================
    # Получить вложение по ID
    # =================================================

    async def get_by_id(
        self,
        attachment_id: int
    ) -> LessonAttachment | None:
        return await self.attachment_repository.get_by_id(
            attachment_id=attachment_id
        )

    # =================================================
    # Получить список
    # =================================================

    async def get_list(
        self,
        lesson_content_id: int | None = None,
        is_visible: bool | None = None,
        uploaded_by: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[LessonAttachment], int]:
        return await self.attachment_repository.get_list(
            lesson_content_id=lesson_content_id,
            is_visible=is_visible,
            uploaded_by=uploaded_by,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Создать вложение
    # =================================================

    async def create(
        self,
        attachment_data: LessonAttachmentCreate
    ) -> LessonAttachment:
        lesson_content = (
            await self.content_repository.get_by_id(
                content_id=(
                    attachment_data.lesson_content_id
                )
            )
        )

        if lesson_content is None:
            raise ValueError(
                "Основной материал занятия не найден"
            )

        user = await validate_content_author(
            user_id=attachment_data.uploaded_by
        )

        if (
            user.get("role") in {"teacher", "TEACHER"}
            and lesson_content.created_by
            != attachment_data.uploaded_by
        ):
            raise ValueError(
                "Преподаватель не является автором "
                "этого материала занятия"
            )

        return await self.attachment_repository.create(
            lesson_content_id=(
                attachment_data.lesson_content_id
            ),
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

    # =================================================
    # Изменить вложение
    # =================================================

    async def update(
        self,
        attachment: LessonAttachment,
        attachment_data: LessonAttachmentUpdate
    ) -> LessonAttachment:
        user = await validate_content_author(
            user_id=attachment_data.updated_by
        )

        if (
            user.get("role") in {"teacher", "TEACHER"}
            and attachment.uploaded_by
            != attachment_data.updated_by
        ):
            raise ValueError(
                "Преподаватель не загружал "
                "это вложение"
            )

        update_data = attachment_data.model_dump(
            exclude_unset=True,
            exclude={
                "updated_by"
            }
        )

        return await self.attachment_repository.update(
            attachment=attachment,
            update_data=update_data
        )

    # =================================================
    # Показать вложение
    # =================================================

    async def show(
        self,
        attachment: LessonAttachment,
        updated_by: int
    ) -> LessonAttachment:
        await self._validate_editor(
            attachment=attachment,
            user_id=updated_by
        )

        if attachment.is_visible:
            raise ValueError(
                "Вложение уже отображается студентам"
            )

        return await self.attachment_repository.set_visibility(
            attachment=attachment,
            is_visible=True
        )

    # =================================================
    # Скрыть вложение
    # =================================================

    async def hide(
        self,
        attachment: LessonAttachment,
        updated_by: int
    ) -> LessonAttachment:
        await self._validate_editor(
            attachment=attachment,
            user_id=updated_by
        )

        if not attachment.is_visible:
            raise ValueError(
                "Вложение уже скрыто"
            )

        return await self.attachment_repository.set_visibility(
            attachment=attachment,
            is_visible=False
        )

    # =================================================
    # Удалить вложение
    # =================================================

    async def delete(
        self,
        attachment: LessonAttachment,
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
    # Проверка пользователя
    # =================================================

    async def _validate_editor(
        self,
        attachment: LessonAttachment,
        user_id: int
    ) -> None:
        user = await validate_content_author(
            user_id=user_id
        )

        if (
            user.get("role") in {"teacher", "TEACHER"}
            and attachment.uploaded_by != user_id
        ):
            raise ValueError(
                "Преподаватель не загружал "
                "это вложение"
            )