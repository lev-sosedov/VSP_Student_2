from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from common.security.dependencies import get_current_principal
from common.security.permissions import require_admin
from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType

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
        "СѓР¶Рµ РїСЂРёРІСЏР·Р°РЅ" in normalized
        or "СѓР¶Рµ Р°РєС‚РёРІРЅР°" in normalized
        or "СѓР¶Рµ РѕС‚РєР»СЋС‡РµРЅР°" in normalized
    ):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )

    if (
        "РЅРµ РЅР°Р№РґРµРЅ" in normalized
        or "РЅРµ РЅР°Р№РґРµРЅР°" in normalized
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
    summary="РџСЂРёРІСЏР·Р°С‚СЊ СЂРѕРґРёС‚РµР»СЏ Рє СЃС‚СѓРґРµРЅС‚Сѓ",
)
async def create_parent_student_link(
    data: ParentStudentLinkCreate,
    db: AsyncSession = Depends(get_db),
    _principal: CurrentPrincipal = Depends(require_admin()),
):
    service = ParentStudentService(db)

    try:
        return await service.create_link(
            parent_id=data.parent_id,
            student_id=data.student_id,
            relationship=data.relationship,
        )

    except ValueError as error:
        raise create_http_exception(error) from error


@router.get(
    "/{link_id}",
    response_model=ParentStudentLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="РџРѕР»СѓС‡РёС‚СЊ СЃРІСЏР·СЊ РїРѕ ID",
)
async def get_parent_student_link(
    link_id: int,
    db: AsyncSession = Depends(get_db),
    principal: CurrentPrincipal = Depends(get_current_principal),
):
    service = ParentStudentService(db)

    try:
        link = await service.get_link(link_id)
        if principal.role is not RoleType.ADMIN and principal.user_id not in {
            link.parent_id,
            link.student_id,
        }:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return link

    except ValueError as error:
        raise create_http_exception(error) from error


@router.get(
    "/parent/{parent_id}",
    response_model=list[
        ParentStudentWithStudentResponse
    ],
    status_code=status.HTTP_200_OK,
    summary="РџРѕР»СѓС‡РёС‚СЊ РґРµС‚РµР№ СЂРѕРґРёС‚РµР»СЏ",
)
async def get_parent_children(
    parent_id: int,
    active_only: bool = Query(
        default=True,
        description=(
            "РџРѕРєР°Р·С‹РІР°С‚СЊ С‚РѕР»СЊРєРѕ Р°РєС‚РёРІРЅС‹Рµ СЃРІСЏР·Рё"
        ),
    ),
    db: AsyncSession = Depends(get_db),
    principal: CurrentPrincipal = Depends(get_current_principal),
):
    if principal.role is not RoleType.ADMIN and (
        principal.role is not RoleType.PARENT or parent_id != principal.user_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    service = ParentStudentService(db)

    try:
        return await service.get_parent_children(
            parent_id=parent_id,
            active_only=active_only,
        )

    except ValueError as error:
        raise create_http_exception(error) from error


@router.get(
    "/student/{student_id}",
    response_model=list[
        ParentStudentWithParentResponse
    ],
    status_code=status.HTTP_200_OK,
    summary="РџРѕР»СѓС‡РёС‚СЊ СЂРѕРґРёС‚РµР»РµР№ СЃС‚СѓРґРµРЅС‚Р°",
)
async def get_student_parents(
    student_id: int,
    active_only: bool = Query(
        default=True,
        description=(
            "РџРѕРєР°Р·С‹РІР°С‚СЊ С‚РѕР»СЊРєРѕ Р°РєС‚РёРІРЅС‹Рµ СЃРІСЏР·Рё"
        ),
    ),
    db: AsyncSession = Depends(get_db),
    principal: CurrentPrincipal = Depends(get_current_principal),
):
    service = ParentStudentService(db)

    try:
        if principal.role is not RoleType.ADMIN and principal.user_id != student_id:
            if principal.role is not RoleType.PARENT:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            links = await service.get_student_parents(student_id=student_id, active_only=True)
            if not any(link.parent_id == principal.user_id for link in links):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return await service.get_student_parents(
            student_id=student_id,
            active_only=active_only,
        )

    except ValueError as error:
        raise create_http_exception(error) from error


@router.patch(
    "/{link_id}",
    response_model=ParentStudentLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="РР·РјРµРЅРёС‚СЊ С‚РёРї СЂРѕРґСЃС‚РІРµРЅРЅРѕР№ СЃРІСЏР·Рё",
)
async def update_parent_student_link(
    link_id: int,
    data: ParentStudentLinkUpdate,
    db: AsyncSession = Depends(get_db),
    _principal: CurrentPrincipal = Depends(require_admin()),
):
    service = ParentStudentService(db)

    try:
        return await service.update_relationship(
            link_id=link_id,
            relationship=data.relationship,
        )

    except ValueError as error:
        raise create_http_exception(error) from error


@router.patch(
    "/{link_id}/activate",
    response_model=ParentStudentLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="Р’РѕСЃСЃС‚Р°РЅРѕРІРёС‚СЊ СЃРІСЏР·СЊ",
)
async def activate_parent_student_link(
    link_id: int,
    db: AsyncSession = Depends(get_db),
    _principal: CurrentPrincipal = Depends(require_admin()),
):
    service = ParentStudentService(db)

    try:
        return await service.activate_link(
            link_id
        )

    except ValueError as error:
        raise create_http_exception(error) from error


@router.delete(
    "/{link_id}",
    response_model=ParentStudentLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="РћС‚РєР»СЋС‡РёС‚СЊ СЃРІСЏР·СЊ СЂРѕРґРёС‚РµР»СЏ Рё СЃС‚СѓРґРµРЅС‚Р°",
)
async def deactivate_parent_student_link(
    link_id: int,
    db: AsyncSession = Depends(get_db),
    _principal: CurrentPrincipal = Depends(require_admin()),
):
    service = ParentStudentService(db)

    try:
        return await service.deactivate_link(
            link_id
        )

    except ValueError as error:
        raise create_http_exception(error) from error
