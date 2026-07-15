from enum import Enum

class LessonType(str, Enum):
    REGULAR = "regular"
    EXTRA = "extra"
    REPLACEMENT = "replacement"
    CONSULTATION = "consultation"
    EXAM = "exam"