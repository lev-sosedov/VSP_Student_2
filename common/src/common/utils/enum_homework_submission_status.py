from enum import StrEnum


class HomeworkSubmissionStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    NEEDS_REVISION = "needs_revision"
    ACCEPTED = "accepted"
    REJECTED = "rejected"