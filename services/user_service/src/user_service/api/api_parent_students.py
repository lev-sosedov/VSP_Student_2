from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.db.db_session import get_db
from user_service.schemas.schemas_parent_student import (
    ParentStudentLinkCreate,
    ParentStudentLinkResponse,
    ParentStudentLinkUpdate,
    ParentStudentWithParentResponse,
    ParentStudentWithStudentResponse,
)
from user_service.services.service_parent_student import (
    ParentStudentService,
)


router = APIRouter(
    prefix="/parent-students",
    tags=["Parent Students"],
)


def create_http_exception(
    error: ValueError,
) -> HTTPException:
    message = str(error)
    normalized = message.lower()

    if (
        "уже привязан" in normalized
        or "уже активна" in normalized
        or "уже отключена" in normalized
    ):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )

    if (
        "не найден" in normalized
        or "не найдена" in normalized
    ):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )

    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )


@router.post(
    "/",
    response_model=ParentStudentLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Привязать родителя к студенту",
)
async def create_parent_student_link(
    data: ParentStudentLinkCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ParentStudentService(db)

    try:
        return await service.create_link(
            parent_id=data.parent_id,
            student_id=data.student_id,
            relationship=data.relationship,
        )

    except ValueError as error:
        raise create_http_exception(error)


@router.get(
    "/{link_id}",
    response_model=ParentStudentLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить связь по ID",
)
async def get_parent_student_link(
    link_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ParentStudentService(db)

    try:
        return await service.get_link(link_id)

    except ValueError as error:
        raise create_http_exception(error)


@router.get(
    "/parent/{parent_id}",
    response_model=list[
        ParentStudentWithStudentResponse
    ],
    status_code=status.HTTP_200_OK,
    summary="Получить детей родителя",
)
async def get_parent_children(
    parent_id: int,
    active_only: bool = Query(
        default=True,
        description=(
            "Показывать только активные связи"
        ),
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ParentStudentService(db)

    try:
        return await service.get_parent_children(
            parent_id=parent_id,
            active_only=active_only,
        )

    except ValueError as error:
        raise create_http_exception(error)


@router.get(
    "/student/{student_id}",
    response_model=list[
        ParentStudentWithParentResponse
    ],
    status_code=status.HTTP_200_OK,
    summary="Получить родителей студента",
)
async def get_student_parents(
    student_id: int,
    active_only: bool = Query(
        default=True,
        description=(
            "Показывать только активные связи"
        ),
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ParentStudentService(db)

    try:
        return await service.get_student_parents(
            student_id=student_id,
            active_only=active_only,
        )

    except ValueError as error:
        raise create_http_exception(error)


@router.patch(
    "/{link_id}",
    response_model=ParentStudentLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="Изменить тип родственной связи",
)
async def update_parent_student_link(
    link_id: int,
    data: ParentStudentLinkUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = ParentStudentService(db)

    try:
        return await service.update_relationship(
            link_id=link_id,
            relationship=data.relationship,
        )

    except ValueError as error:
        raise create_http_exception(error)


@router.patch(
    "/{link_id}/activate",
    response_model=ParentStudentLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="Восстановить связь",
)
async def activate_parent_student_link(
    link_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ParentStudentService(db)

    try:
        return await service.activate_link(
            link_id
        )

    except ValueError as error:
        raise create_http_exception(error)


@router.delete(
    "/{link_id}",
    response_model=ParentStudentLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="Отключить связь родителя и студента",
)
async def deactivate_parent_student_link(
    link_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ParentStudentService(db)

    try:
        return await service.deactivate_link(
            link_id
        )

    except ValueError as error:
        raise create_http_exception(error)