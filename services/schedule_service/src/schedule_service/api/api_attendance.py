from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_attendance_status import (
    AttendanceStatus,
)
from schedule_service.db.db_session import (
    get_session,
)
from schedule_service.schemas.schemas_attendance import (
    AttendanceCreate,
    AttendanceListResponse,
    AttendanceResponse,
    AttendanceUpdate,
)
from schedule_service.services.service_attendance import (
    create_attendance,
    get_attendance_by_id,
    get_attendance_by_lesson_and_student,
    get_attendance_records,
    get_lesson_for_attendance,
    update_attendance,
)


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)


@router.post(
    "",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать отметку посещаемости",
)
async def create_attendance_endpoint(
    attendance_data: AttendanceCreate,
    session: AsyncSession = Depends(get_session),
):
    lesson = await get_lesson_for_attendance(
        session=session,
        lesson_id=attendance_data.lesson_id,
    )

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено",
        )

    existing = (
        await get_attendance_by_lesson_and_student(
            session=session,
            lesson_id=attendance_data.lesson_id,
            student_id=attendance_data.student_id,
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Посещаемость этого студента "
                "на данном занятии уже отмечена"
            ),
        )

    try:
        return await create_attendance(
            session=session,
            attendance_data=attendance_data,
        )

    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Не удалось создать отметку "
                "посещаемости"
            ),
        ) from error


@router.get(
    "",
    response_model=AttendanceListResponse,
    summary="Получить список посещаемости",
)
async def get_attendance_endpoint(
    lesson_id: int | None = Query(
        default=None,
        gt=0,
    ),
    student_id: int | None = Query(
        default=None,
        gt=0,
    ),
    attendance_status: AttendanceStatus | None = Query(
        default=None,
        alias="status",
    ),
    marked_by: int | None = Query(
        default=None,
        gt=0,
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    session: AsyncSession = Depends(get_session),
):
    records, total = await get_attendance_records(
        session=session,
        lesson_id=lesson_id,
        student_id=student_id,
        attendance_status=attendance_status,
        marked_by=marked_by,
        skip=skip,
        limit=limit,
    )

    return AttendanceListResponse(
        total=total,
        items=records,
    )


@router.get(
    "/lesson/{lesson_id}",
    response_model=AttendanceListResponse,
    summary="Получить посещаемость занятия",
)
async def get_lesson_attendance_endpoint(
    lesson_id: int,
    session: AsyncSession = Depends(get_session),
):
    lesson = await get_lesson_for_attendance(
        session=session,
        lesson_id=lesson_id,
    )

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено",
        )

    records, total = await get_attendance_records(
        session=session,
        lesson_id=lesson_id,
        skip=0,
        limit=500,
    )

    return AttendanceListResponse(
        total=total,
        items=records,
    )


@router.get(
    "/student/{student_id}",
    response_model=AttendanceListResponse,
    summary="Получить посещаемость студента",
)
async def get_student_attendance_endpoint(
    student_id: int,
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    session: AsyncSession = Depends(get_session),
):
    records, total = await get_attendance_records(
        session=session,
        student_id=student_id,
        skip=skip,
        limit=limit,
    )

    return AttendanceListResponse(
        total=total,
        items=records,
    )


@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Получить отметку посещаемости",
)
async def get_attendance_by_id_endpoint(
    attendance_id: int,
    session: AsyncSession = Depends(get_session),
):
    attendance = await get_attendance_by_id(
        session=session,
        attendance_id=attendance_id,
    )

    if attendance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отметка посещаемости не найдена",
        )

    return attendance


@router.patch(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Изменить отметку посещаемости",
)
async def update_attendance_endpoint(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    session: AsyncSession = Depends(get_session),
):
    attendance = await get_attendance_by_id(
        session=session,
        attendance_id=attendance_id,
    )

    if attendance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отметка посещаемости не найдена",
        )

    return await update_attendance(
        session=session,
        attendance=attendance,
        attendance_data=attendance_data,
    )