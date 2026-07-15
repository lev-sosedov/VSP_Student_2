from fastapi import APIRouter, Depends, HTTPException, status

from academic_service.services.service_group_member import GroupMemberService

from academic_service.schemas.schemas_group_member import (
    GroupMemberCreate,
    GroupMemberUpdate,
    GroupMemberPatch,
    GroupMemberResponse,
    GroupMemberExistsResponse,
    GroupMemberLeave,
    GroupMemberTransfer
)

from academic_service.core.core_dependencies import get_group_member_service

router = APIRouter(
    prefix="/group-members",
    tags=["Group Members"]
)


# =========================
# Добавить участника в группу
# =========================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=GroupMemberResponse,
    summary="Добавление участника в группу",
    description="""
Добавляет пользователя в учебную группу.

Во время добавления:

- проверяется существование группы;
- проверяется активность группы;
- проверяется, не состоит ли пользователь уже в группе;
- сохраняется роль пользователя в группе.

Допустимые роли:

- student;
- teacher.

Данные пользователя хранятся в User Service.
В Academic Service сохраняется только идентификатор пользователя.
""",
    response_description="Добавленный участник группы",
    responses={
        201: {
            "description": "Участник успешно добавлен"
        },
        400: {
            "description": "Группа закрыта или пользователь уже состоит в группе"
        },
        404: {
            "description": "Группа не найдена"
        },
        422: {
            "description": "Ошибка валидации данных"
        }
    }
)
async def add_member(
        data: GroupMemberCreate,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.add_member(data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Перевести участника между группами
# =========================
@router.post(
    "/transfer",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberResponse,
    summary="Перевод участника между группами",
    description="""
Переводит пользователя из одной учебной группы в другую.

Во время перевода:

- проверяется существующая связь пользователя с прежней группой;
- проверяется существование новой группы;
- проверяется активность новой группы;
- изменяется принадлежность пользователя к группе.
""",
    response_description="Обновленная запись участника",
    responses={
        400: {
            "description": "Перевод невозможен"
        },
        404: {
            "description": "Участник или новая группа не найдены"
        },
        422: {
            "description": "Ошибка валидации данных"
        }
    }
)
async def transfer_member(
        data: GroupMemberTransfer,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.transfer_member(data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Проверить участие пользователя
# =========================
@router.get(
    "/check/{group_id}/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberExistsResponse,
    summary="Проверить участие пользователя в группе",
    description="""
Проверяет, состоит ли пользователь в указанной учебной группе.

Учитываются только активные записи участников.
""",
    response_description="Результат проверки участия"
)
async def check_member(
        group_id: int,
        user_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        exists = await service.is_member(
            group_id,
            user_id
        )

        return {
            "exists": exists
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Получить участников группы
# =========================
@router.get(
    "/group/{group_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[GroupMemberResponse],
    summary="Получить участников группы",
    description="""
Возвращает список всех активных участников выбранной группы.

В список могут входить:

- студенты;
- преподаватели.
""",
    response_description="Список участников группы",
    responses={
        404: {
            "description": "Группа не найдена"
        }
    }
)
async def get_group_members(
        group_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.get_group_members(group_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Получить преподавателя группы
# =========================
@router.get(
    "/group/{group_id}/teacher",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberResponse | None,
    summary="Получить преподавателя группы",
    description="""
Возвращает активного преподавателя выбранной группы.

Если преподаватель не назначен, возвращается пустой результат.
""",
    response_description="Преподаватель группы",
    responses={
        404: {
            "description": "Группа или преподаватель не найдены"
        }
    }
)
async def get_teacher(
        group_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.get_teacher(group_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Назначить преподавателя
# =========================
@router.post(
    "/group/{group_id}/teacher/{user_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=GroupMemberResponse,
    summary="Назначить преподавателя",
    description="""
Добавляет пользователя в группу с ролью teacher.

Во время назначения:

- проверяется существование группы;
- проверяется активность группы;
- проверяется отсутствие активной связи пользователя с группой.
""",
    response_description="Назначенный преподаватель",
    responses={
        201: {
            "description": "Преподаватель успешно назначен"
        },
        400: {
            "description": "Пользователь уже состоит в группе"
        },
        404: {
            "description": "Группа не найдена"
        }
    }
)
async def assign_teacher(
        group_id: int,
        user_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.assign_teacher(
            group_id,
            user_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Назначить студента
# =========================
@router.post(
    "/group/{group_id}/student/{user_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=GroupMemberResponse,
    summary="Назначить студента",
    description="""
Добавляет пользователя в группу с ролью student.

Во время назначения:

- проверяется существование группы;
- проверяется активность группы;
- проверяется отсутствие активной связи пользователя с группой.
""",
    response_description="Добавленный студент",
    responses={
        201: {
            "description": "Студент успешно добавлен"
        },
        400: {
            "description": "Пользователь уже состоит в группе"
        },
        404: {
            "description": "Группа не найдена"
        }
    }
)
async def assign_student(
        group_id: int,
        user_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.assign_student(
            group_id,
            user_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Общее количество участников
# =========================
@router.get(
    "/group/{group_id}/count",
    status_code=status.HTTP_200_OK,
    summary="Получить количество участников",
    description="""
Возвращает общее количество активных участников группы.

Учитываются:

- студенты;
- преподаватели.
""",
    response_description="Количество участников группы",
    responses={
        404: {
            "description": "Группа не найдена"
        }
    }
)
async def count_members(
        group_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return {
            "members": await service.count_members(group_id)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Количество студентов
# =========================
@router.get(
    "/group/{group_id}/count/students",
    status_code=status.HTTP_200_OK,
    summary="Получить количество студентов",
    description="""
Возвращает количество активных студентов выбранной группы.
""",
    response_description="Количество студентов группы",
    responses={
        404: {
            "description": "Группа не найдена"
        }
    }
)
async def count_students(
        group_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return {
            "students": await service.count_students(group_id)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Количество преподавателей
# =========================
@router.get(
    "/group/{group_id}/count/teachers",
    status_code=status.HTTP_200_OK,
    summary="Получить количество преподавателей",
    description="""
Возвращает количество активных преподавателей выбранной группы.
""",
    response_description="Количество преподавателей группы",
    responses={
        404: {
            "description": "Группа не найдена"
        }
    }
)
async def count_teachers(
        group_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return {
            "teachers": await service.count_teachers(group_id)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Получить группы пользователя
# =========================
@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[GroupMemberResponse],
    summary="Получить группы пользователя",
    description="""
Возвращает список активных связей пользователя с учебными группами.

Пользователь может состоять в нескольких группах.
""",
    response_description="Список групп пользователя"
)
async def get_user_groups(
        user_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.get_user_groups(user_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Получить участника по ID
# =========================
@router.get(
    "/{member_id}",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberResponse,
    summary="Получить участника группы",
    description="""
Возвращает запись участника группы по идентификатору связи.

member_id — это идентификатор записи таблицы group_members,
а не идентификатор пользователя.
""",
    response_description="Информация об участнике группы",
    responses={
        404: {
            "description": "Участник не найден"
        }
    }
)
async def get_member(
        member_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.get_member(member_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Полностью обновить участника
# =========================
@router.put(
    "/{member_id}",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberResponse,
    summary="Полностью обновить участника",
    description="""
Полное обновление записи участника группы.

Можно изменить:

- учебную группу;
- пользователя;
- роль пользователя в группе.
""",
    response_description="Обновленная запись участника",
    responses={
        404: {
            "description": "Участник или группа не найдены"
        },
        422: {
            "description": "Ошибка валидации данных"
        }
    }
)
async def update_member(
        member_id: int,
        data: GroupMemberUpdate,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.update_member(
            member_id,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Частично обновить участника
# =========================
@router.patch(
    "/{member_id}",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberResponse,
    summary="Частично обновить участника",
    description="""
Частичное обновление записи участника группы.

Можно изменить:

- роль;
- статус активности.

Передаются только изменяемые поля.
""",
    response_description="Обновленная запись участника",
    responses={
        404: {
            "description": "Участник не найден"
        },
        422: {
            "description": "Ошибка валидации данных"
        }
    }
)
async def patch_member(
        member_id: int,
        data: GroupMemberPatch,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.patch_member(
            member_id,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Исключить участника из группы
# =========================
@router.delete(
    "/{member_id}",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberResponse,
    summary="Исключить участника из группы",
    description="""
Выполняет мягкое удаление участника.

После операции:

- запись сохраняется в базе данных;
- участник становится неактивным;
- сохраняется дата выхода из группы.
""",
    response_description="Неактивная запись участника",
    responses={
        404: {
            "description": "Участник не найден"
        }
    }
)
async def remove_member(
        member_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.remove_member(member_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Восстановить участника
# =========================
@router.post(
    "/{member_id}/restore",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberResponse,
    summary="Восстановить участника",
    description="""
Восстанавливает ранее исключенного участника.

После восстановления:

- запись становится активной;
- дата выхода очищается.
""",
    response_description="Восстановленный участник",
    responses={
        404: {
            "description": "Участник не найден"
        }
    }
)
async def restore_member(
        member_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.restore_member(member_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Выход пользователя из группы
# =========================
@router.post(
    "/{member_id}/leave",
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberResponse,
    summary="Оформить выход участника из группы",
    description="""
Переводит участника в неактивный статус
с указанием даты выхода из группы.

Используется при:

- отчислении;
- завершении обучения;
- самостоятельном выходе пользователя.
""",
    response_description="Неактивная запись участника",
    responses={
        404: {
            "description": "Участник не найден"
        },
        422: {
            "description": "Ошибка валидации даты выхода"
        }
    }
)
async def leave_group(
        member_id: int,
        data: GroupMemberLeave,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.leave_group(
            member_id,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Полностью удалить запись
# =========================
@router.delete(
    "/{member_id}/hard",
    status_code=status.HTTP_200_OK,
    summary="Полностью удалить запись участника",
    description="""
Полностью удаляет запись участника из базы данных.

В отличие от обычного удаления:

- запись не сохраняется;
- восстановить участника через эту запись будет невозможно.

Используется только администраторами.
""",
    response_description="Результат полного удаления",
    responses={
        404: {
            "description": "Участник не найден"
        }
    }
)
async def delete_member(
        member_id: int,
        service: GroupMemberService = Depends(get_group_member_service)
):
    try:
        return await service.delete_member(member_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
