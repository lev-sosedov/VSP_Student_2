from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from common.utils.enum_schedule_change_type import ScheduleChangeType


# =====================================================
# Ответ с историей изменения
# =====================================================

class ScheduleChangeResponse(BaseModel):
    id: int
    lesson_id: int

    change_type: ScheduleChangeType

    old_data: dict[str, Any] | None
    new_data: dict[str, Any] | None

    reason: str | None
    changed_by: int
    comment: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Список изменений
# =====================================================

class ScheduleChangeListResponse(BaseModel):
    total: int
    items: list[ScheduleChangeResponse]