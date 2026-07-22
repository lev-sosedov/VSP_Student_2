from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_homework_submission_status import (
    HomeworkSubmissionStatus
)
from content_service.db.db_session import get_session
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
from content_service.services.service_homework_submission import (
    HomeworkSubmissionService
)


router = APIRouter(
    prefix="/homework-submissions",
    tags=["Homework submissions"]
)


# =====================================================
# Создать черновик работы
# =====================================================

@router.post(
    "",
    response_model=HomeworkSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать черновик домашней работы"
)
async def create_homework_submission_endpoint(
    submission_data: HomeworkSubmissionCreate,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    try:
        return await service.create(
            submission_data=submission_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить список работ
# =====================================================

@router.get(
    "",
    response_model=HomeworkSubmissionListResponse,
    summary="Получить список домашних работ"
)
async def get_homework_submissions_endpoint(
    homework_id: int | None = Query(
        default=None,
        gt=0
    ),
    student_id: int | None = Query(
        default=None,
        gt=0
    ),
    group_id: int | None = Query(
        default=None,
        gt=0
    ),
    submission_status: (
        HomeworkSubmissionStatus | None
    ) = Query(
        default=None,
        alias="status"
    ),
    is_late: bool | None = Query(
        default=None
    ),
    checked_by: int | None = Query(
        default=None,
        gt=0
    ),
    skip: int = Query(
        default=0,
        ge=0
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500
    ),
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    submissions, total = await service.get_list(
        homework_id=homework_id,
        student_id=student_id,
        group_id=group_id,
        submission_status=submission_status,
        is_late=is_late,
        checked_by=checked_by,
        skip=skip,
        limit=limit
    )

    return HomeworkSubmissionListResponse(
        total=total,
        items=submissions
    )


# =====================================================
# Получить работы по домашнему заданию
# До маршрута /{submission_id}
# =====================================================

@router.get(
    "/homework/{homework_id}",
    response_model=HomeworkSubmissionListResponse,
    summary="Получить работы по домашнему заданию"
)
async def get_submissions_by_homework_endpoint(
    homework_id: int,
    submission_status: (
        HomeworkSubmissionStatus | None
    ) = Query(
        default=None,
        alias="status"
    ),
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    submissions, total = await service.get_list(
        homework_id=homework_id,
        submission_status=submission_status,
        skip=0,
        limit=500
    )

    return HomeworkSubmissionListResponse(
        total=total,
        items=submissions
    )


# =====================================================
# Получить работы студента
# =====================================================

@router.get(
    "/student/{student_id}",
    response_model=HomeworkSubmissionListResponse,
    summary="Получить домашние работы студента"
)
async def get_submissions_by_student_endpoint(
    student_id: int,
    submission_status: (
        HomeworkSubmissionStatus | None
    ) = Query(
        default=None,
        alias="status"
    ),
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    submissions, total = await service.get_list(
        student_id=student_id,
        submission_status=submission_status,
        skip=0,
        limit=500
    )

    return HomeworkSubmissionListResponse(
        total=total,
        items=submissions
    )


# =====================================================
# Получить работу по ID
# =====================================================

@router.get(
    "/{submission_id}",
    response_model=HomeworkSubmissionResponse,
    summary="Получить домашнюю работу по ID"
)
async def get_homework_submission_endpoint(
    submission_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    submission = await service.get_by_id(
        submission_id=submission_id
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашняя работа не найдена"
        )

    return submission


# =====================================================
# Изменить ответ студента
# =====================================================

@router.patch(
    "/{submission_id}",
    response_model=HomeworkSubmissionResponse,
    summary="Изменить черновик домашней работы"
)
async def update_homework_submission_endpoint(
    submission_id: int,
    submission_data: HomeworkSubmissionUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    submission = await service.get_by_id(
        submission_id=submission_id
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашняя работа не найдена"
        )

    try:
        return await service.update(
            submission=submission,
            submission_data=submission_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Отправить работу
# =====================================================

@router.post(
    "/{submission_id}/submit",
    response_model=HomeworkSubmissionResponse,
    summary="Отправить работу преподавателю"
)
async def submit_homework_submission_endpoint(
    submission_id: int,
    submit_data: HomeworkSubmissionSubmitRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    submission = await service.get_by_id(
        submission_id=submission_id
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашняя работа не найдена"
        )

    try:
        return await service.submit(
            submission=submission,
            student_id=submit_data.student_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Начать проверку
# =====================================================

@router.post(
    "/{submission_id}/start-review",
    response_model=HomeworkSubmissionResponse,
    summary="Начать проверку домашней работы"
)
async def start_review_endpoint(
    submission_id: int,
    review_data: HomeworkSubmissionReviewRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    submission = await service.get_by_id(
        submission_id=submission_id
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашняя работа не найдена"
        )

    try:
        return await service.start_review(
            submission=submission,
            checked_by=review_data.checked_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Вернуть на доработку
# =====================================================

@router.post(
    "/{submission_id}/request-revision",
    response_model=HomeworkSubmissionResponse,
    summary="Вернуть работу на доработку"
)
async def request_revision_endpoint(
    submission_id: int,
    revision_data: HomeworkSubmissionRevisionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    submission = await service.get_by_id(
        submission_id=submission_id
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашняя работа не найдена"
        )

    try:
        return await service.request_revision(
            submission=submission,
            checked_by=revision_data.checked_by,
            teacher_comment=(
                revision_data.teacher_comment
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Принять работу
# =====================================================

@router.post(
    "/{submission_id}/accept",
    response_model=HomeworkSubmissionResponse,
    summary="Принять домашнюю работу"
)
async def accept_submission_endpoint(
    submission_id: int,
    accept_data: HomeworkSubmissionAcceptRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    submission = await service.get_by_id(
        submission_id=submission_id
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашняя работа не найдена"
        )

    try:
        return await service.accept(
            submission=submission,
            accept_data=accept_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Отклонить работу
# =====================================================

@router.post(
    "/{submission_id}/reject",
    response_model=HomeworkSubmissionResponse,
    summary="Отклонить домашнюю работу"
)
async def reject_submission_endpoint(
    submission_id: int,
    reject_data: HomeworkSubmissionRejectRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkSubmissionService(
        session=session
    )

    submission = await service.get_by_id(
        submission_id=submission_id
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашняя работа не найдена"
        )

    try:
        return await service.reject(
            submission=submission,
            reject_data=reject_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error