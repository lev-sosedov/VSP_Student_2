from datetime import datetime

from academic_service.repositories.direction_repository import DirectionRepository
from academic_service.repositories.education_plan_repository import EducationPlanRepository
from academic_service.schemas.direction import (DirectionCreate, DirectionUpdate, DirectionPatch)


class DirectionService:


    def __init__(self,repo: DirectionRepository,plan_repo: EducationPlanRepository):
        self.repo = repo
        self.plan_repo = plan_repo


    # создать направление
    async def create_direction(self, data: DirectionCreate):
        existing = await self.repo.get_by_name(data.name)

        if existing:
            raise ValueError("Direction already exists")

        return await self.repo.create(data)


    # получить по id
    async def get_by_id(self, direction_id: int):
        direction = await self.repo.get_by_id(direction_id)

        if not direction:
            raise ValueError("Direction not found")

        return direction


    # получить по имени
    async def get_by_name(self, name: str):

        return await self.repo.get_by_name(name)


    # список направлений
    async def get_all(self, limit: int = 20, offset: int = 0):

        return await self.repo.get_all(limit=limit, offset=offset)


    # обновление
    async def update(self, direction_id: int, data: DirectionUpdate):
        direction = await self.get_by_id(direction_id)


        if data.name is not None:
            exists = await self.repo.get_by_name(data.name)
            if exists and exists.id != direction_id:
                raise ValueError("Direction name already exists")

            direction.name = data.name

        if data.description is not None:
            direction.description = data.description

        return await self.repo.update(direction)


    # PATCH
    async def patch(self, direction_id: int, data: DirectionPatch):
        direction = await self.get_by_id(direction_id)

        if data.name is not None:
            exists = await self.repo.get_by_name(data.name)
            if exists and exists.id != direction_id:
                raise ValueError("Direction name already exists")

            direction.name = data.name

        if data.description is not None:
            direction.description = data.description

        if data.is_active is not None:
            direction.is_active = data.is_active

        return await self.repo.update(direction)


    # активировать
    async def activate(self, direction_id: int):
        direction = await self.get_by_id(direction_id)
        direction.is_active = True
        direction.closed_at = None

        return await self.repo.update(direction)


    # деактивировать (архив)
    async def deactivate(self, direction_id: int):
        direction = await self.get_by_id(direction_id)
        direction.is_active = False
        direction.closed_at = datetime.utcnow()

        return await self.repo.update(direction)


    # мягкое удаление (проверка зависимостей)
    async def delete(self, direction_id: int):
        direction = await self.get_by_id(direction_id)
        plans = await self.plan_repo.get_by_direction(direction_id)

        if plans:
            raise ValueError(
                "Direction has education plans and cannot be deleted"
            )

        return await self.repo.delete(direction_id)


    # направление + планы
    async def get_with_plans(self, direction_id: int):
        direction = await self.get_by_id(direction_id)
        plans = await self.plan_repo.get_by_direction(direction_id)

        return {"direction": direction, "education_plans": plans}


    # только активные
    async def get_active(self):

        return await self.repo.get_active()


    # архивные
    async def get_closed(self):

        return await self.repo.get_closed()


    # проверка существует ли
    async def exists(self, direction_id: int):
        direction = await self.repo.get_by_id(direction_id)

        return direction is not None


    # поиск
    async def search(self, query: str):

        return await self.repo.search(query)


    # количество планов
    async def count_plans(self, direction_id: int):
        plans = await self.plan_repo.get_by_direction(direction_id)

        return len(plans)


    # безопасное удаление
    async def safe_delete(self, direction_id: int):
        plans = await self.plan_repo.get_by_direction(direction_id)

        if plans:
            raise ValueError("Cannot delete direction with education plans")

        return await self.repo.delete(direction_id)