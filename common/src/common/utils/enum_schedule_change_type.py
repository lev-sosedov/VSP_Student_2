from enum import Enum


class ScheduleChangeType(str, Enum):
    RESCHEDULED = "rescheduled"           # Перенос даты или времени
    CANCELLED = "cancelled"               # Отмена занятия
    TEACHER_CHANGED = "teacher_changed"   # Замена преподавателя
    ROOM_CHANGED = "room_changed"         # Замена кабинета
    UPDATED = "updated"                   # Изменение темы, описания и других данных
    RESTORED = "restored"                 # Восстановление отменённого занятия