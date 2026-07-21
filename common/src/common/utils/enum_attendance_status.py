from enum import Enum


class AttendanceStatus(str, Enum):
    PRESENT = "present" # присутствовал
    ABSENT = "absent" # отсутствовал
    LATE = "late" # опоздал
    EXCUSED = "excused" # отсутствовал по уважительной причине