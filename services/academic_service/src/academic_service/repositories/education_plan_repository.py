from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from academic_service.models.education_plans import EducationPlan



class EducationPlanRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    # Создание учебного плана
    async def create(self,plan: EducationPlan):
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)

        return plan


    # Получение по id
    async def get_by_id(self,plan_id: int):
        result = await self.db.execute(select(EducationPlan).where(EducationPlan.id == plan_id))

        return result.scalar_one_or_none()


    # Все учебные планы
    async def get_all(self):
        result = await self.db.execute(select(EducationPlan).order_by(EducationPlan.id))

        return result.scalars().all()


    # Все планы конкретного направления
    async def get_by_direction(self,direction_id: int):
        result = await self.db.execute(select(EducationPlan).where(EducationPlan.direction_id == direction_id))

        return result.scalars().all()


    # Только активные
    async def get_active(self):
        result = await self.db.execute(select(EducationPlan).where(EducationPlan.is_active == True).order_by(EducationPlan.duration_months))

        return result.scalars().all()


    # Только закрытые
    async def get_closed(self):
        result = await self.db.execute(select(EducationPlan).where(EducationPlan.is_active == False))

        return result.scalars().all()


    # Поиск по названию
    async def search_by_name(self,name: str):
        result = await self.db.execute(select(EducationPlan).where(EducationPlan.name.ilike(f"%{name}%")))

        return result.scalars().all()


    # Проверка существования
    async def exists(self,plan_id: int):
        result = await self.db.execute(select(EducationPlan.id).where(EducationPlan.id == plan_id))

        return result.scalar_one_or_none() is not None


    # Проверка плана по направлению
    async def exists_for_direction(self,direction_id: int,duration_months: int):
        result = await self.db.execute(select(EducationPlan.id).where(EducationPlan.direction_id == direction_id,EducationPlan.duration_months == duration_months))

        return result.scalar_one_or_none() is not None


    # Обновление
    async def update(self,plan_id: int,data: dict):
        await self.db.execute(update(EducationPlan).where(EducationPlan.id == plan_id).values(**data))
        await self.db.commit()

        return await self.get_by_id(plan_id)


    # Изменить длительность курса
    async def update_duration(self,plan_id: int,months: int):
        await self.db.execute(update(EducationPlan).where(EducationPlan.id == plan_id).values(duration_months=months))
        await self.db.commit()

        return await self.get_by_id(plan_id)


    # Изменить количество занятий в неделю
    async def update_lessons_per_week(self,plan_id: int,count: int):
        await self.db.execute(update(EducationPlan).where(EducationPlan.id == plan_id).values(lessons_per_week=count))
        await self.db.commit()

        return await self.get_by_id(plan_id)


    # Закрыть учебный план
    async def deactivate(self,plan_id: int):
        plan = await self.get_by_id(plan_id)

        if plan:
            plan.is_active = False
            await self.db.commit()

        return plan


    # Открыть учебный план
    async def activate(self,plan_id: int):
        plan = await self.get_by_id(plan_id)

        if plan:
            plan.is_active = True
            await self.db.commit()

        return plan


    # Удаление
    async def delete(self,plan_id: int):
        await self.db.execute(delete(EducationPlan).where(EducationPlan.id == plan_id))
        await self.db.commit()