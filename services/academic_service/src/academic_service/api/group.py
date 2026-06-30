from fastapi import APIRouter, Depends, Query

from academic_service.services.group_service import GroupService
from academic_service.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupPatch,
    GroupResponse,
    GroupDetailResponse,
    GroupListResponse,
    GroupExistsResponse
)

from academic_service.core.dependencies import get_group_service


router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)


# Создание группы
@router.post("/", response_model=GroupResponse)
async def create_group(
        data: GroupCreate,
        service: GroupService = Depends(get_group_service)
):
    return await service.create_group(data)



# Получение группы по ID
@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.get_group(group_id)



# Получение детальной информации о группе
@router.get("/{group_id}/detail", response_model=GroupDetailResponse)
async def get_group_detail(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.get_group_detail(group_id)



# Получение списка групп
@router.get("/", response_model=GroupListResponse)
async def get_groups(
        limit: int = Query(20, ge=1),
        offset: int = Query(0, ge=0),
        service: GroupService = Depends(get_group_service)
):
    groups = await service.get_groups(
        limit=limit,
        offset=offset
    )

    return {
        "items": groups,
        "total": len(groups)
    }



# Получение активных групп
@router.get("/active/list")
async def get_active_groups(
        service: GroupService = Depends(get_group_service)
):
    return await service.get_active_groups()



# Получение закрытых групп
@router.get("/closed/list")
async def get_closed_groups(
        service: GroupService = Depends(get_group_service)
):
    return await service.get_closed_groups()



# Обновление группы
@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
        group_id: int,
        data: GroupUpdate,
        service: GroupService = Depends(get_group_service)
):
    return await service.update_group(
        group_id,
        data
    )



# Частичное обновление группы
@router.patch("/{group_id}", response_model=GroupResponse)
async def patch_group(
        group_id: int,
        data: GroupPatch,
        service: GroupService = Depends(get_group_service)
):
    return await service.patch_group(
        group_id,
        data
    )



# Закрытие группы
@router.post("/{group_id}/close")
async def close_group(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.close_group(group_id)



# Восстановление группы
@router.post("/{group_id}/restore")
async def restore_group(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.restore_group(group_id)



# Удаление группы
@router.delete("/{group_id}")
async def delete_group(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.delete_group(group_id)



# Безопасное удаление группы
@router.delete("/{group_id}/safe")
async def safe_delete_group(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.safe_delete_group(group_id)



# Проверка существования группы
@router.get("/{group_id}/exists", response_model=GroupExistsResponse)
async def exists_group(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    result = await service.exists(group_id)

    return {
        "exists": result
    }



# Поиск групп по названию
@router.get("/search/name")
async def search_groups(
        name: str,
        service: GroupService = Depends(get_group_service)
):
    return await service.search(name)



# Группы филиала
@router.get("/branch/{branch_id}")
async def get_groups_by_branch(
        branch_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.get_by_branch(branch_id)



# Группы направления
@router.get("/direction/{direction_id}")
async def get_groups_by_direction(
        direction_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.get_by_direction(direction_id)



# Группы учебного плана
@router.get("/plan/{plan_id}")
async def get_groups_by_plan(
        plan_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.get_by_plan(plan_id)



# Количество студентов в группе
@router.get("/{group_id}/students/count")
async def count_students(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.count_students(group_id)



# Количество преподавателей
@router.get("/{group_id}/teachers/count")
async def count_teachers(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.count_teachers(group_id)



# Добавить пользователя в группу
@router.post("/{group_id}/members")
async def add_member(
        group_id: int,
        user_id: int,
        role: str,
        service: GroupService = Depends(get_group_service)
):
    return await service.add_member(
        group_id,
        user_id,
        role
    )



# Удалить пользователя из группы
@router.delete("/{group_id}/members/{user_id}")
async def remove_member(
        group_id: int,
        user_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.remove_member(
        group_id,
        user_id
    )