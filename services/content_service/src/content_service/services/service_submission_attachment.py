from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_homework_submission_status import (
    HomeworkSubmissionStatus
)
from content_service.models.model_submission_attachment import (
    SubmissionAttachment
)
from content_service.repositories.repository_homework_submission import (
    HomeworkSubmissionRepository
)
from content_service.repositories.repository_submission_attachment import (
    SubmissionAttachmentRepository
)
from content_service.schemas.schemas_submission_attachment import (
    SubmissionAttachmentCreate,
    SubmissionAttachmentUpdate
)
from content_service.services.service_external_validation import (
    validate_student
)


class SubmissionAttachmentService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.attachment_repository = (
            SubmissionAttachmentRepository(
                session=session
            )
        )

        self.submission_repository = (
            HomeworkSubmissionRepository(
                session=session
            )
        )

    # =================================================
    # Получить файл по ID
    # =================================================

    async def get_by_id(
        self,
        attachment_id: int
    ) -> SubmissionAttachment | None:
        return await (
            self.attachment_repository.get_by_id(
                attachment_id=attachment_id
            )
        )

    # =================================================
    # Получить список файлов
    # =================================================

    async def get_list(
        self,
        submission_id: int | None = None,
        uploaded_by: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[SubmissionAttachment], int]:
        return await (
            self.attachment_repository.get_list(
                submission_id=submission_id,
                uploaded_by=uploaded_by,
                skip=skip,
                limit=limit
            )
        )

    # =================================================
    # Создать файл
    # =================================================

    async def create(
        self,
        attachment_data: SubmissionAttachmentCreate
    ) -> SubmissionAttachment:
        submission = (
            await self.submission_repository.get_by_id(
                submission_id=(
                    attachment_data.submission_id
                )
            )
        )

        if submission is None:
            raise ValueError(
                "Домашняя работа не найдена"
            )

        await self._validate_student_owner(
            submission_student_id=(
                submission.student_id
            ),
            user_id=attachment_data.uploaded_by
        )

        if submission.status not in {
            HomeworkSubmissionStatus.DRAFT,
            HomeworkSubmissionStatus.NEEDS_REVISION
        }:
            raise ValueError(
                "Добавлять файлы можно только "
                "в черновик или работу на доработке"
            )

        return await (
            self.attachment_repository.create(
                submission_id=(
                    attachment_data.submission_id
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
                uploaded_by=attachment_data.uploaded_by
            )
        )

    # =================================================
    # Изменить файл
    # =================================================

    async def update(
        self,
        attachment: SubmissionAttachment,
        attachment_data: SubmissionAttachmentUpdate
    ) -> SubmissionAttachment:
        submission = (
            await self.submission_repository.get_by_id(
                submission_id=attachment.submission_id
            )
        )

        if submission is None:
            raise ValueError(
                "Домашняя работа не найдена"
            )

        await self._validate_student_owner(
            submission_student_id=(
                submission.student_id
            ),
            user_id=attachment_data.updated_by
        )

        if submission.status not in {
            HomeworkSubmissionStatus.DRAFT,
            HomeworkSubmissionStatus.NEEDS_REVISION
        }:
            raise ValueError(
                "Изменять файлы можно только "
                "в черновике или работе на доработке"
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
    # Удалить файл
    # =================================================

    async def delete(
        self,
        attachment: SubmissionAttachment,
        deleted_by: int
    ) -> None:
        submission = (
            await self.submission_repository.get_by_id(
                submission_id=attachment.submission_id
            )
        )

        if submission is None:
            raise ValueError(
                "Домашняя работа не найдена"
            )

        await self._validate_student_owner(
            submission_student_id=(
                submission.student_id
            ),
            user_id=deleted_by
        )

        if submission.status not in {
            HomeworkSubmissionStatus.DRAFT,
            HomeworkSubmissionStatus.NEEDS_REVISION
        }:
            raise ValueError(
                "Удалять файлы можно только "
                "из черновика или работы на доработке"
            )

        await self.attachment_repository.delete(
            attachment_id=attachment.id
        )

    # =================================================
    # Проверка владельца работы
    # =================================================

    async def _validate_student_owner(
        self,
        submission_student_id: int,
        user_id: int
    ) -> None:
        await validate_student(
            student_id=user_id
        )

        if submission_student_id != user_id:
            raise ValueError(
                "Студент не является владельцем "
                "этой домашней работы"
            )