from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from common.utils.enum_attendance_status import (
    AttendanceStatus,
)


class AttendanceCreate(BaseModel):
    lesson_id: int = Field(
        ...,
        gt=0,
        description="ID конкретного занятия",
    )

    student_id: int = Field(
        ...,
        gt=0,
        description="ID студента из user-service",
    )

    status: AttendanceStatus = Field(
        default=AttendanceStatus.PRESENT,
        description="Статус посещаемости",
    )

    late_minutes: int = Field(
        default=0,
        ge=0,
        le=1440,
        description="Количество минут опоздания",
    )

    comment: str | None = Field(
        default=None,
        max_length=1000,
        description="Комментарий преподавателя",
    )

    marked_by: int = Field(
        ...,
        gt=0,
        description="ID преподавателя или администратора",
    )

    @model_validator(mode="after")
    def validate_late_minutes(self):
        if self.status != AttendanceStatus.LATE:
            self.late_minutes = 0

        if (
            self.status == AttendanceStatus.LATE
            and self.late_minutes <= 0
        ):
            raise ValueError(
                "Для статуса late укажите количество минут опоздания"
            )

        return self


class AttendanceUpdate(BaseModel):
    status: AttendanceStatus | None = None

    late_minutes: int | None = Field(
        default=None,
        ge=0,
        le=1440,
    )

    comment: str | None = Field(
        default=None,
        max_length=1000,
    )

    marked_by: int = Field(
        ...,
        gt=0,
        description="ID пользователя, изменившего отметку",
    )

    @model_validator(mode="after")
    def validate_late_minutes(self):
        if (
            self.status == AttendanceStatus.LATE
            and (
                self.late_minutes is None
                or self.late_minutes <= 0
            )
        ):
            raise ValueError(
                "Для статуса late укажите количество минут опоздания"
            )

        if (
            self.status is not None
            and self.status != AttendanceStatus.LATE
        ):
            self.late_minutes = 0

        return self


class AttendanceResponse(BaseModel):
    id: int

    lesson_id: int
    student_id: int

    status: AttendanceStatus
    late_minutes: int
    comment: str | None

    marked_by: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AttendanceListResponse(BaseModel):
    total: int
    items: list[AttendanceResponse]