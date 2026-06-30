from datetime import datetime

from academic_service.repositories.education_plan_repository import EducationPlanRepository
from academic_service.repositories.direction_repository import DirectionRepository
from academic_service.repositories.education_plan_module_repository import EducationPlanModuleRepository
from academic_service.repositories.module_repository import ModuleRepository
from academic_service.schemas.education_plan import (EducationPlanCreate, EducationPlanUpdate, EducationPlanPatch)


class EducationPlanService:

    def __init__(
            self,
            plan_repo: EducationPlanRepository,
            direction_repo: DirectionRepository,
            plan_module_repo: EducationPlanModuleRepository,
            module_repo: ModuleRepository
    ):
        self.plan_repo = plan_repo
        self.direction_repo = direction_repo
        self.plan_module_repo = plan_module_repo
        self.module_repo = module_repo


    # создать учебный план
    async def create_education_plan(self, data: EducationPlanCreate):
        direction = await self.direction_repo.get_by_id(data.direction_id)

        if not direction:
            raise ValueError("Direction not found")

        if not direction.is_active:
            raise ValueError("Direction is inactive")

        existing = await self.plan_repo.get_by_name(data.name)

        if existing:
            raise ValueError("Education plan already exists")

        return await self.plan_repo.create(data)



    # получить план
    async def get_plan_by_id(self, plan_id:int):
        plan = await self.plan_repo.get_by_id(plan_id)

        if not plan:
            raise ValueError("Education plan not found")

        return plan



    # получить все планы
    async def get_all(self,limit:int = 20,offset:int = 0):

        return await self.plan_repo.get_all( limit,offset)


    # планы конкретного направления
    async def get_by_direction(self,direction_id:int):
        direction = await self.direction_repo.get_by_id(direction_id)

        if not direction:
            raise ValueError("Direction not found")

        return await self.plan_repo.get_by_direction(direction_id)


    # обновление полностью
    async def update_plan(self,plan_id:int,data:EducationPlanUpdate):
        plan = await self.get_plan_by_id(plan_id)

        if data.direction_id:
            direction = await self.direction_repo.get_by_id(data.direction_id)
            if not direction:
                raise ValueError("Direction not found")
            plan.direction_id = data.direction_id

        if data.name:
            plan.name = data.name

        if data.duration_months:
            plan.duration_months = data.duration_months

        if data.lessons_per_week:
            plan.lessons_per_week = data.lessons_per_week

        return await self.plan_repo.update(plan)


    # PATCH
    async def patch_plan(self,plan_id:int,data:EducationPlanPatch):
        plan = await self.get_plan_by_id(plan_id)

        if data.direction_id is not None:
            direction = await self.direction_repo.get_by_id(data.direction_id)
            if not direction:
                raise ValueError("Direction not found")
            plan.direction_id = data.direction_id

        if data.name is not None:
            plan.name = data.name

        if data.duration_months is not None:
            plan.duration_months = data.duration_months

        if data.lessons_per_week is not None:
            plan.lessons_per_week = data.lessons_per_week

        if data.is_active is not None:
            plan.is_active = data.is_active

        return await self.plan_repo.update(plan)




    # добавить модуль
    async def add_module(self,plan_id:int, module_id:int,order_number:int):
        plan = await self.get_plan_by_id(plan_id)
        module = await self.module_repo.get_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        exists = await self.plan_module_repo.get_by_plan_and_module(plan_id,module_id)

        if exists:
            raise ValueError("Module already added")

        return await self.plan_module_repo.create(plan_id,module_id,order_number)




    # удалить модуль
    async def remove_module(self,plan_id:int,module_id:int):
        item = await self.plan_module_repo.get_by_plan_and_module(plan_id, module_id)

        if not item:
            raise ValueError("Module not found")

        return await self.plan_module_repo.delete(item.id)


    # список модулей плана
    async def get_modules(self,plan_id:int):
        await self.get_plan_by_id(plan_id)

        return await self.plan_module_repo.get_modules_by_plan(plan_id)


    # изменить порядок модулей
    async def reorder_modules(self,plan_id:int,items:list[dict]):
        await self.get_plan_by_id(plan_id)

        for item in items:
            link = await self.plan_module_repo.get_by_plan_and_module(plan_id,item["module_id"])

            if not link:
                raise ValueError("Module not found in plan")

            link.order_number = item["order_number"]
            await self.plan_module_repo.update(link)

        return await self.get_modules(plan_id)


    # активировать
    async def activate_plan(self,plan_id:int):
        plan = await self.get_plan_by_id(plan_id)
        plan.is_active = True
        plan.closed_at = None

        return await self.plan_repo.update(plan)




    # закрыть план
    async def close_plan(self,plan_id:int):
        plan = await self.get_plan_by_id(plan_id)
        plan.is_active = False
        plan.closed_at = datetime.utcnow()

        return await self.plan_repo.update(plan)


    # удалить полностью
    async def delete_plan(self, plan_id:int):
        plan = await self.get_plan_by_id(plan_id)
        used = await self.plan_module_repo.is_plan_used(plan_id)

        if used:
            raise ValueError("Plan is used")

        return await self.plan_repo.delete(plan_id)


    # безопасное удаление
    async def safe_delete(self,plan_id:int):
        modules = await self.plan_module_repo.get_modules_by_plan(plan_id)

        if modules:
            raise ValueError("Remove modules first")

        return await self.delete_plan(plan_id)


    # копирование плана
    async def clone_plan(self,source_plan_id:int,new_name:str):
        source = await self.get_plan_by_id( source_plan_id)
        new_plan = await self.plan_repo.create(
            EducationPlanCreate(
                direction_id=source.direction_id,
                name=new_name,
                duration_months=source.duration_months,
                lessons_per_week=source.lessons_per_week))

        modules = await self.plan_module_repo.get_modules_by_plan(source_plan_id)

        for item in modules:
            await self.plan_module_repo.create(new_plan.id,item.module_id,item.order_number)

        return new_plan


    # количество модулей
    async def count_modules(self,plan_id:int):
        modules = await self.get_modules(plan_id)

        return len(modules)