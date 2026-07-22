from datetime import datetime

from sqlalchemy import func, select
from content_service.models.model_homework import Homework
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_homework_submission_status import (
    HomeworkSubmissionStatus
)
from content_service.models.model_homework_submission import (
    HomeworkSubmission
)


class HomeworkSubmissionRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить работу по ID
    # =================================================

    async def get_by_id(
        self,
        submission_id: int
    ) -> HomeworkSubmission | None:
        query = select(HomeworkSubmission).where(
            HomeworkSubmission.id == submission_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить работу студента по заданию
    # =================================================

    async def get_by_homework_and_student(
        self,
        homework_id: int,
        student_id: int
    ) -> HomeworkSubmission | None:
        query = select(HomeworkSubmission).where(
            HomeworkSubmission.homework_id == homework_id,
            HomeworkSubmission.student_id == student_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить список работ
    # =================================================

    async def get_list(
            self,
            homework_id: int | None = None,
            student_id: int | None = None,
            group_id: int | None = None,
            submission_status: (
                    HomeworkSubmissionStatus | None
            ) = None,
            is_late: bool | None = None,
            checked_by: int | None = None,
            skip: int = 0,
            limit: int = 100
    ) -> tuple[list[HomeworkSubmission], int]:
        filters = []

        if homework_id is not None:
            filters.append(
                HomeworkSubmission.homework_id == homework_id
            )

        if student_id is not None:
            filters.append(
                HomeworkSubmission.student_id == student_id
            )

        if group_id is not None:
            filters.append(
                Homework.group_id == group_id
            )

        if submission_status is not None:
            filters.append(
                HomeworkSubmission.status == submission_status
            )

        if is_late is not None:
            filters.append(
                HomeworkSubmission.is_late == is_late
            )

        if checked_by is not None:
            filters.append(
                HomeworkSubmission.checked_by == checked_by
            )

        submissions_query = (
            select(HomeworkSubmission)
            .join(
                Homework,
                Homework.id == HomeworkSubmission.homework_id
            )
            .where(*filters)
            .order_by(
                HomeworkSubmission.submitted_at.desc(),
                HomeworkSubmission.created_at.desc(),
                HomeworkSubmission.id.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(HomeworkSubmission.id))
            .join(
                Homework,
                Homework.id == HomeworkSubmission.homework_id
            )
            .where(*filters)
        )

        submissions_result = await self.session.execute(
            submissions_query
        )

        count_result = await self.session.execute(
            count_query
        )

        submissions = list(
            submissions_result.scalars().all()
        )

        total = count_result.scalar_one()

        return submissions, total

    # =================================================
    # Создать черновик
    # =================================================

    async def create(
        self,
        homework_id: int,
        student_id: int,
        answer_text: str | None
    ) -> HomeworkSubmission:
        submission = HomeworkSubmission(
            homework_id=homework_id,
            student_id=student_id,
            answer_text=answer_text,
            status=HomeworkSubmissionStatus.DRAFT,
            is_late=False
        )

        self.session.add(submission)

        await self.session.flush()
        await self.session.refresh(submission)

        return submission

    # =================================================
    # Изменить текст ответа
    # =================================================

    async def update_answer(
        self,
        submission: HomeworkSubmission,
        answer_text: str | None
    ) -> HomeworkSubmission:
        submission.answer_text = answer_text

        await self.session.flush()
        await self.session.refresh(submission)

        return submission

    # =================================================
    # Отправить работу
    # =================================================

    async def submit(
        self,
        submission: HomeworkSubmission,
        submitted_at: datetime,
        is_late: bool
    ) -> HomeworkSubmission:
        submission.status = (
            HomeworkSubmissionStatus.SUBMITTED
        )

        submission.submitted_at = submitted_at
        submission.is_late = is_late

        # После повторной отправки сбрасываем
        # старое решение преподавателя.
        submission.score = None
        submission.teacher_comment = None
        submission.checked_by = None
        submission.checked_at = None

        await self.session.flush()
        await self.session.refresh(submission)

        return submission

    # =================================================
    # Начать проверку
    # =================================================

    async def start_review(
        self,
        submission: HomeworkSubmission,
        checked_by: int
    ) -> HomeworkSubmission:
        submission.status = (
            HomeworkSubmissionStatus.IN_REVIEW
        )

        submission.checked_by = checked_by
        submission.checked_at = None

        await self.session.flush()
        await self.session.refresh(submission)

        return submission

    # =================================================
    # Записать результат проверки
    # =================================================

    async def set_review_result(
        self,
        submission: HomeworkSubmission,
        submission_status: HomeworkSubmissionStatus,
        checked_by: int,
        teacher_comment: str | None,
        score: int | None,
        checked_at: datetime
    ) -> HomeworkSubmission:
        submission.status = submission_status
        submission.checked_by = checked_by
        submission.teacher_comment = teacher_comment
        submission.score = score
        submission.checked_at = checked_at

        await self.session.flush()
        await self.session.refresh(submission)

        return submission