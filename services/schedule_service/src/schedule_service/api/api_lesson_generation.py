from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_service.db.db_session import get_session
from schedule_service.schemas.schemas_lesson_generation import (
    LessonGenerationRequest,
    LessonGenerationResponse
)
from schedule_service.services.service_lesson_generation import (
    generate_lessons_from_template
)
from schedule_service.services.service_schedule_template import (
    get_active_room_by_id,
    get_schedule_template_by_id
)


router = APIRouter(
    prefix="/schedule-templates",
    tags=["Lesson generation"]
)


# =====================================================
# Генерация занятий по недельному шаблону
# =====================================================

@router.post(
    "/{template_id}/generate-lessons",
    response_model=LessonGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Сформировать занятия по недельному шаблону"
)
async def generate_lessons_endpoint(
    template_id: int,
    generation_data: LessonGenerationRequest,
    session: AsyncSession = Depends(get_session)
):
    template = await get_schedule_template_by_id(
        session=session,
        template_id=template_id
    )

    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон расписания не найден"
        )

    if not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Нельзя формировать занятия "
                "по неактивному шаблону"
            )
        )

    room = await get_active_room_by_id(
        session=session,
        room_id=template.room_id
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Нельзя сформировать занятия: "
                "кабинет не существует или неактивен"
            )
        )

    try:
        result = await generate_lessons_from_template(
            session=session,
            template=template,
            generation_data=generation_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

    return result