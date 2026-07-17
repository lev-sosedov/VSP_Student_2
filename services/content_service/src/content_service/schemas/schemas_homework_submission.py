from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)

from common.utils.enum_homework_submission_status import (
    HomeworkSubmissionStatus
)


# =====================================================
# Создание черновика работы
# =====================================================

class HomeworkSubmissionCreate(BaseModel):
    homework_id: int = Field(
        ...,
        gt=0,
        description="ID домашнего задания"
    )

    student_id: int = Field(
        ...,
        gt=0,
        description=(
            "ID студента. Позже будет получаться из JWT"
        )
    )

    answer_text: str | None = Field(
        default=None,
        max_length=20000,
        description="Текстовый ответ студента"
    )

    @field_validator("answer_text")
    @classmethod
    def clean_answer_text(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


# =====================================================
# Изменение черновика или работы на доработке
# =====================================================

class HomeworkSubmissionUpdate(BaseModel):
    answer_text: str | None = Field(
        default=None,
        max_length=20000
    )

    student_id: int = Field(
        ...,
        gt=0,
        description=(
            "ID студента, изменяющего работу. "
            "Позже будет получаться из JWT"
        )
    )

    @field_validator("answer_text")
    @classmethod
    def clean_answer_text(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


# =====================================================
# Отправка работы преподавателю
# =====================================================

class HomeworkSubmissionSubmitRequest(BaseModel):
    student_id: int = Field(
        ...,
        gt=0,
        description=(
            "ID студента, отправляющего работу. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Начало проверки преподавателем
# =====================================================

class HomeworkSubmissionReviewRequest(BaseModel):
    checked_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID преподавателя. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Возврат на доработку
# =====================================================

class HomeworkSubmissionRevisionRequest(BaseModel):
    checked_by: int = Field(
        ...,
        gt=0
    )

    teacher_comment: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Что студенту необходимо исправить"
    )

    @field_validator("teacher_comment")
    @classmethod
    def validate_comment(
        cls,
        value: str
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Комментарий преподавателя "
                "не может быть пустым"
            )

        return cleaned_value


# =====================================================
# Принятие работы
# =====================================================

class HomeworkSubmissionAcceptRequest(BaseModel):
    checked_by: int = Field(
        ...,
        gt=0
    )

    score: int = Field(
        ...,
        ge=0,
        description="Количество набранных баллов"
    )

    teacher_comment: str | None = Field(
        default=None,
        max_length=10000
    )

    @field_validator("teacher_comment")
    @classmethod
    def clean_comment(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


# =====================================================
# Отклонение работы
# =====================================================

class HomeworkSubmissionRejectRequest(BaseModel):
    checked_by: int = Field(
        ...,
        gt=0
    )

    teacher_comment: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Причина отклонения работы"
    )

    score: int | None = Field(
        default=None,
        ge=0
    )

    @field_validator("teacher_comment")
    @classmethod
    def validate_comment(
        cls,
        value: str
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Причина отклонения не может быть пустой"
            )

        return cleaned_value


# =====================================================
# Ответ API
# =====================================================

class HomeworkSubmissionResponse(BaseModel):
    id: int

    homework_id: int
    student_id: int

    answer_text: str | None

    status: HomeworkSubmissionStatus

    score: int | None
    teacher_comment: str | None
    checked_by: int | None

    is_late: bool

    submitted_at: datetime | None
    checked_at: datetime | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Ответ со списком работ
# =====================================================

class HomeworkSubmissionListResponse(BaseModel):
    total: int
    items: list[HomeworkSubmissionResponse]