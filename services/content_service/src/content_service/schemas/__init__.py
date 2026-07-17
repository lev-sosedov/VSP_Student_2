from content_service.schemas.schemas_lesson_content import (
    LessonContentCreate,
    LessonContentListResponse,
    LessonContentPublicationRequest,
    LessonContentResponse,
    LessonContentUpdate
)
from content_service.schemas.schemas_lesson_attachment import (
    LessonAttachmentCreate,
    LessonAttachmentDeleteResponse,
    LessonAttachmentListResponse,
    LessonAttachmentResponse,
    LessonAttachmentUpdate,
    LessonAttachmentVisibilityRequest
)
from content_service.schemas.schemas_lesson_link import (
    LessonLinkCreate,
    LessonLinkDeleteResponse,
    LessonLinkListResponse,
    LessonLinkResponse,
    LessonLinkUpdate,
    LessonLinkVisibilityRequest
)
from content_service.schemas.schemas_homework import (
    HomeworkActivityRequest,
    HomeworkCreate,
    HomeworkListResponse,
    HomeworkPublicationRequest,
    HomeworkResponse,
    HomeworkUpdate
)
from content_service.schemas.schemas_homework_attachment import (
    HomeworkAttachmentCreate,
    HomeworkAttachmentDeleteResponse,
    HomeworkAttachmentListResponse,
    HomeworkAttachmentResponse,
    HomeworkAttachmentUpdate,
    HomeworkAttachmentVisibilityRequest
)
from content_service.schemas.schemas_homework_submission import (
    HomeworkSubmissionAcceptRequest,
    HomeworkSubmissionCreate,
    HomeworkSubmissionListResponse,
    HomeworkSubmissionRejectRequest,
    HomeworkSubmissionResponse,
    HomeworkSubmissionReviewRequest,
    HomeworkSubmissionRevisionRequest,
    HomeworkSubmissionSubmitRequest,
    HomeworkSubmissionUpdate
)
from content_service.schemas.schemas_submission_attachment import (
    SubmissionAttachmentCreate,
    SubmissionAttachmentDeleteResponse,
    SubmissionAttachmentListResponse,
    SubmissionAttachmentResponse,
    SubmissionAttachmentUpdate
)



__all__ = [
    "LessonContentCreate",
    "LessonContentUpdate",
    "LessonContentPublicationRequest",
    "LessonContentResponse",
    "LessonContentListResponse",
    "LessonAttachmentCreate",
    "LessonAttachmentUpdate",
    "LessonAttachmentVisibilityRequest",
    "LessonAttachmentResponse",
    "LessonAttachmentListResponse",
    "LessonAttachmentDeleteResponse",
    "LessonLinkCreate",
    "LessonLinkUpdate",
    "LessonLinkVisibilityRequest",
    "LessonLinkResponse",
    "LessonLinkListResponse",
    "LessonLinkDeleteResponse",
    "HomeworkCreate",
    "HomeworkUpdate",
    "HomeworkPublicationRequest",
    "HomeworkActivityRequest",
    "HomeworkResponse",
    "HomeworkListResponse",
    "HomeworkAttachmentCreate",
    "HomeworkAttachmentUpdate",
    "HomeworkAttachmentVisibilityRequest",
    "HomeworkAttachmentResponse",
    "HomeworkAttachmentListResponse",
    "HomeworkAttachmentDeleteResponse",
    "HomeworkSubmissionCreate",
    "HomeworkSubmissionUpdate",
    "HomeworkSubmissionSubmitRequest",
    "HomeworkSubmissionReviewRequest",
    "HomeworkSubmissionRevisionRequest",
    "HomeworkSubmissionAcceptRequest",
    "HomeworkSubmissionRejectRequest",
    "HomeworkSubmissionResponse",
    "HomeworkSubmissionListResponse",
    "SubmissionAttachmentCreate",
    "SubmissionAttachmentUpdate",
    "SubmissionAttachmentResponse",
    "SubmissionAttachmentListResponse",
    "SubmissionAttachmentDeleteResponse",
]