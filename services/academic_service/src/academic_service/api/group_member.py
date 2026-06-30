from fastapi import APIRouter, Depends

from academic_service.services.group_member_service import GroupMemberService
from academic_service.schemas.group_member import (
    GroupMemberCreate,
    GroupMemberUpdate,
    GroupMemberPatch,
    GroupMemberFilter,
    GroupMemberLeave,
    GroupMemberActivate,
    GroupMemberTransfer,
    GroupMemberBulkCreate
)

from academic_service.core.dependencies import get_group_member_service


router = APIRouter(
    prefix="/group-members",
    tags=["Group Members"]
)


# Добавление участника в группу
@router.post("/")
async def add_member(
    data: GroupMemberCreate,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.add_member(data)



# Получить участника по ID
@router.get("/{member_id}")
async def get_member(
    member_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.get_member(member_id)



# Получить всех участников группы
@router.get("/group/{group_id}")
async def get_group_members(
    group_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.get_group_members(group_id)



# Получить группы пользователя
@router.get("/user/{user_id}")
async def get_user_groups(
    user_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.get_user_groups(user_id)



# Получить преподавателя группы
@router.get("/group/{group_id}/teacher")
async def get_teacher(
    group_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.get_teacher(group_id)



# Назначить преподавателя
@router.post("/group/{group_id}/teacher/{user_id}")
async def assign_teacher(
    group_id: int,
    user_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.assign_teacher(group_id, user_id)



# Назначить студента
@router.post("/group/{group_id}/student/{user_id}")
async def assign_student(
    group_id: int,
    user_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.assign_student(group_id, user_id)



# Изменить роль участника
@router.patch("/{member_id}/role")
async def change_role(
    member_id: int,
    role: str,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.change_role(member_id, role)



# Полное обновление участника
@router.put("/{member_id}")
async def update_member(
    member_id: int,
    data: GroupMemberUpdate,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.update_member(member_id, data)



# Частичное обновление участника
@router.patch("/{member_id}")
async def patch_member(
    member_id: int,
    data: GroupMemberPatch,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.patch_member(member_id, data)



# Удалить участника из группы (soft delete)
@router.delete("/{member_id}")
async def remove_member(
    member_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.remove_member(member_id)



# Полное удаление записи
@router.delete("/{member_id}/hard")
async def delete_member(
    member_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.delete_member(member_id)



# Восстановить участника
@router.post("/{member_id}/restore")
async def restore_member(
    member_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.restore_member(member_id)



# Активировать участника
@router.post("/{member_id}/activate")
async def activate_member(
    member_id: int,
    data: GroupMemberActivate,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.activate_member(member_id, data)



# Выход пользователя из группы
@router.post("/{member_id}/leave")
async def leave_group(
    member_id: int,
    data: GroupMemberLeave,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.leave_group(member_id, data)



# Проверка состоит ли пользователь в группе
@router.get("/check/{group_id}/{user_id}")
async def check_member(
    group_id: int,
    user_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    exists = await service.is_member(group_id, user_id)

    return {
        "exists": exists
    }



# Фильтрация участников
@router.post("/filter")
async def filter_members(
    data: GroupMemberFilter,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.filter_members(data)



# Перевод между группами
@router.post("/transfer")
async def transfer_member(
    data: GroupMemberTransfer,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.transfer_member(data)



# Массовое добавление
@router.post("/bulk")
async def bulk_create(
    data: GroupMemberBulkCreate,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return await service.bulk_create(data)



# Количество студентов
@router.get("/group/{group_id}/count/students")
async def count_students(
    group_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return {
        "students": await service.count_students(group_id)
    }



# Количество преподавателей
@router.get("/group/{group_id}/count/teachers")
async def count_teachers(
    group_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return {
        "teachers": await service.count_teachers(group_id)
    }



# Общее количество участников
@router.get("/group/{group_id}/count")
async def count_members(
    group_id: int,
    service: GroupMemberService = Depends(get_group_member_service)
):
    return {
        "members": await service.count_members(group_id)
    }