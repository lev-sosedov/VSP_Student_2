from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_homework_submission_status import (
    HomeworkSubmissionStatus
)
from content_service.models.model_homework_submission import (
    HomeworkSubmission
)
from content_service.repositories.repository_homework import (
    HomeworkRepository
)
from content_service.repositories.repository_homework_submission import (
    HomeworkSubmissionRepository
)
from content_service.schemas.schemas_homework_submission import (
    HomeworkSubmissionAcceptRequest,
    HomeworkSubmissionCreate,
    HomeworkSubmissionRejectRequest,
    HomeworkSubmissionUpdate
)
from content_service.services.service_external_validation import (
    validate_content_author,
    validate_lesson,
    validate_student,
    validate_student_group_membership
)
from content_service.messaging.messaging_event_publisher import (
    content_event_publisher
)


class HomeworkSubmissionService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.submission_repository = (
            HomeworkSubmissionRepository(
                session=session
            )
        )

        self.homework_repository = HomeworkRepository(
            session=session
        )

    # =================================================
    # Получить работу по ID
    # =================================================

    async def get_by_id(
        self,
        submission_id: int
    ) -> HomeworkSubmission | None:
        return await self.submission_repository.get_by_id(
            submission_id=submission_id
        )

    # =================================================
    # Получить список
    # =================================================

    async def get_list(
        self,
        homework_id: int | None = None,
        student_id: int | None = None,
        submission_status: (
            HomeworkSubmissionStatus | None
        ) = None,
        is_late: bool | None = None,
        checked_by: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[HomeworkSubmission], int]:
        return await self.submission_repository.get_list(
            homework_id=homework_id,
            student_id=student_id,
            submission_status=submission_status,
            is_late=is_late,
            checked_by=checked_by,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Создать черновик
    # =================================================

    async def create(
        self,
        submission_data: HomeworkSubmissionCreate
    ) -> HomeworkSubmission:
        await validate_student(
            student_id=submission_data.student_id
        )

        homework = await self.homework_repository.get_by_id(
            homework_id=submission_data.homework_id
        )

        if homework is None:
            raise ValueError(
                "Домашнее задание не найдено"
            )

        if not homework.is_active:
            raise ValueError(
                "Домашнее задание неактивно"
            )

        if not homework.is_published:
            raise ValueError(
                "Домашнее задание ещё не опубликовано"
            )

        lesson = await validate_lesson(
            lesson_id=homework.lesson_id
        )

        await validate_student_group_membership(
            student_id=submission_data.student_id,
            group_id=lesson["group_id"]
        )

        existing_submission = (
            await self.submission_repository
            .get_by_homework_and_student(
                homework_id=submission_data.homework_id,
                student_id=submission_data.student_id
            )
        )

        if existing_submission is not None:
            raise ValueError(
                "Работа студента по этому заданию "
                "уже создана"
            )

        return await self.submission_repository.create(
            homework_id=submission_data.homework_id,
            student_id=submission_data.student_id,
            answer_text=submission_data.answer_text
        )

    # =================================================
    # Изменить работу студентом
    # =================================================

    async def update(
        self,
        submission: HomeworkSubmission,
        submission_data: HomeworkSubmissionUpdate
    ) -> HomeworkSubmission:
        await self._validate_student_owner(
            submission=submission,
            student_id=submission_data.student_id
        )

        if submission.status not in {
            HomeworkSubmissionStatus.DRAFT,
            HomeworkSubmissionStatus.NEEDS_REVISION
        }:
            raise ValueError(
                "Изменять можно только черновик "
                "или работу, возвращённую на доработку"
            )

        return await (
            self.submission_repository.update_answer(
                submission=submission,
                answer_text=submission_data.answer_text
            )
        )

    # =================================================
    # Отправить работу преподавателю
    # =================================================

    async def submit(
        self,
        submission: HomeworkSubmission,
        student_id: int
    ) -> HomeworkSubmission:
        await self._validate_student_owner(
            submission=submission,
            student_id=student_id
        )

        if submission.status not in {
            HomeworkSubmissionStatus.DRAFT,
            HomeworkSubmissionStatus.NEEDS_REVISION
        }:
            raise ValueError(
                "Эта работа уже отправлена "
                "или проверена"
            )

        homework = await self.homework_repository.get_by_id(
            homework_id=submission.homework_id
        )

        if homework is None:
            raise ValueError(
                "Домашнее задание не найдено"
            )

        if not homework.is_active:
            raise ValueError(
                "Домашнее задание неактивно"
            )

        if not homework.is_published:
            raise ValueError(
                "Домашнее задание не опубликовано"
            )

        has_answer = bool(
            submission.answer_text
            and submission.answer_text.strip()
        )

        # Пока файлы работы ещё не подключены,
        # поэтому требуется текстовый ответ.
        if not has_answer:
            raise ValueError(
                "Перед отправкой заполните текстовый ответ"
            )

        submitted_at = self._utc_now_naive()

        is_late = False

        if homework.due_at is not None:
            due_at = self._to_naive_utc(
                homework.due_at
            )

            is_late = submitted_at > due_at

            if (
                is_late
                and not homework.allow_late_submission
            ):
                raise ValueError(
                    "Срок сдачи истёк, поздняя отправка "
                    "запрещена"
                )

        submission = await self.submission_repository.submit(
            submission=submission,
            submitted_at=submitted_at,
            is_late=is_late
        )

        await content_event_publisher.publish(
            routing_key="content.submission.submitted",
            payload={
                "submission_id": submission.id,
                "homework_id": submission.homework_id,
                "student_id": submission.student_id,
                "is_late": submission.is_late,
                "submitted_at": submission.submitted_at
            }
        )

        return submission

    # =================================================
    # Начать проверку
    # =================================================

    async def start_review(
        self,
        submission: HomeworkSubmission,
        checked_by: int
    ) -> HomeworkSubmission:
        await self._validate_teacher(
            submission=submission,
            teacher_id=checked_by
        )

        if (
            submission.status
            != HomeworkSubmissionStatus.SUBMITTED
        ):
            raise ValueError(
                "Начать проверку можно только "
                "для отправленной работы"
            )

        submission = (
            await self.submission_repository.start_review(
                submission=submission,
                checked_by=checked_by
            )
        )

        await content_event_publisher.publish(
            routing_key="content.submission.in_review",
            payload={
                "submission_id": submission.id,
                "homework_id": submission.homework_id,
                "student_id": submission.student_id,
                "checked_by": checked_by
            }
        )

        return submission

    # =================================================
    # Вернуть работу на доработку
    # =================================================

    async def request_revision(
        self,
        submission: HomeworkSubmission,
        checked_by: int,
        teacher_comment: str
    ) -> HomeworkSubmission:
        await self._validate_teacher(
            submission=submission,
            teacher_id=checked_by
        )

        if submission.status not in {
            HomeworkSubmissionStatus.SUBMITTED,
            HomeworkSubmissionStatus.IN_REVIEW
        }:
            raise ValueError(
                "На доработку можно вернуть только "
                "отправленную или проверяемую работу"
            )

        submission = await (
            self.submission_repository.set_review_result(
                submission=submission,
                submission_status=(
                    HomeworkSubmissionStatus.NEEDS_REVISION
                ),
                checked_by=checked_by,
                teacher_comment=teacher_comment,
                score=None,
                checked_at=self._utc_now_naive()
            )
        )

        await content_event_publisher.publish(
            routing_key=(
                "content.submission.needs_revision"
            ),
            payload={
                "submission_id": submission.id,
                "homework_id": submission.homework_id,
                "student_id": submission.student_id,
                "checked_by": checked_by,
                "teacher_comment": teacher_comment,
                "checked_at": submission.checked_at
            }
        )

        return submission

    # =================================================
    # Принять работу
    # =================================================

    async def accept(
        self,
        submission: HomeworkSubmission,
        accept_data: HomeworkSubmissionAcceptRequest
    ) -> HomeworkSubmission:
        await self._validate_teacher(
            submission=submission,
            teacher_id=accept_data.checked_by
        )

        if submission.status not in {
            HomeworkSubmissionStatus.SUBMITTED,
            HomeworkSubmissionStatus.IN_REVIEW
        }:
            raise ValueError(
                "Принять можно только отправленную "
                "или проверяемую работу"
            )

        homework = await self.homework_repository.get_by_id(
            homework_id=submission.homework_id
        )

        if homework is None:
            raise ValueError(
                "Домашнее задание не найдено"
            )

        if accept_data.score > homework.max_score:
            raise ValueError(
                f"Оценка не может превышать "
                f"{homework.max_score} баллов"
            )

        submission = await (
            self.submission_repository.set_review_result(
                submission=submission,
                submission_status=(
                    HomeworkSubmissionStatus.ACCEPTED
                ),
                checked_by=accept_data.checked_by,
                teacher_comment=(
                    accept_data.teacher_comment
                ),
                score=accept_data.score,
                checked_at=self._utc_now_naive()
            )
        )

        await content_event_publisher.publish(
            routing_key="content.submission.accepted",
            payload={
                "submission_id": submission.id,
                "homework_id": submission.homework_id,
                "student_id": submission.student_id,
                "checked_by": accept_data.checked_by,
                "score": submission.score,
                "teacher_comment": (
                    submission.teacher_comment
                ),
                "checked_at": submission.checked_at
            }
        )

        return submission

    # =================================================
    # Отклонить работу
    # =================================================

    async def reject(
        self,
        submission: HomeworkSubmission,
        reject_data: HomeworkSubmissionRejectRequest
    ) -> HomeworkSubmission:
        await self._validate_teacher(
            submission=submission,
            teacher_id=reject_data.checked_by
        )

        if submission.status not in {
            HomeworkSubmissionStatus.SUBMITTED,
            HomeworkSubmissionStatus.IN_REVIEW
        }:
            raise ValueError(
                "Отклонить можно только отправленную "
                "или проверяемую работу"
            )

        homework = await self.homework_repository.get_by_id(
            homework_id=submission.homework_id
        )

        if homework is None:
            raise ValueError(
                "Домашнее задание не найдено"
            )

        if (
            reject_data.score is not None
            and reject_data.score > homework.max_score
        ):
            raise ValueError(
                f"Оценка не может превышать "
                f"{homework.max_score} баллов"
            )

        submission = await (
            self.submission_repository.set_review_result(
                submission=submission,
                submission_status=(
                    HomeworkSubmissionStatus.REJECTED
                ),
                checked_by=reject_data.checked_by,
                teacher_comment=(
                    reject_data.teacher_comment
                ),
                score=reject_data.score,
                checked_at=self._utc_now_naive()
            )
        )

        await content_event_publisher.publish(
            routing_key="content.submission.rejected",
            payload={
                "submission_id": submission.id,
                "homework_id": submission.homework_id,
                "student_id": submission.student_id,
                "checked_by": reject_data.checked_by,
                "score": submission.score,
                "teacher_comment": (
                    submission.teacher_comment
                ),
                "checked_at": submission.checked_at
            }
        )

        return submission

    # =================================================
    # Проверить владельца-студента
    # =================================================

    async def _validate_student_owner(
        self,
        submission: HomeworkSubmission,
        student_id: int
    ) -> None:
        await validate_student(
            student_id=student_id
        )

        if submission.student_id != student_id:
            raise ValueError(
                "Студент не является владельцем "
                "этой работы"
            )

    # =================================================
    # Проверить преподавателя
    # =================================================

    async def _validate_teacher(
        self,
        submission: HomeworkSubmission,
        teacher_id: int
    ) -> None:
        user = await validate_content_author(
            user_id=teacher_id
        )

        # Администратор может проверить любую работу.
        if user.get("role") in {
            "admin",
            "ADMIN"
        }:
            return

        homework = await self.homework_repository.get_by_id(
            homework_id=submission.homework_id
        )

        if homework is None:
            raise ValueError(
                "Домашнее задание не найдено"
            )

        if homework.created_by != teacher_id:
            raise ValueError(
                "Преподаватель не является автором "
                "этого домашнего задания"
            )

    # =================================================
    # Текущее UTC-время без timezone
    # =================================================

    @staticmethod
    def _utc_now_naive() -> datetime:
        return datetime.now(
            timezone.utc
        ).replace(
            tzinfo=None
        )

    # =================================================
    # Приведение даты к naive UTC
    # =================================================

    @staticmethod
    def _to_naive_utc(
        value: datetime
    ) -> datetime:
        if value.tzinfo is None:
            return value

        return value.astimezone(
            timezone.utc
        ).replace(
            tzinfo=None
        )