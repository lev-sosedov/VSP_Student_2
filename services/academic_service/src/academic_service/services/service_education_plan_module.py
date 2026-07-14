from academic_service.repositories.repository_education_plan_module import EducationPlanModuleRepository
from academic_service.repositories.repository_education_plan import EducationPlanRepository
from academic_service.repositories.repository_module import ModuleRepository

from academic_service.schemas.schemas_education_plan_module import (
    EducationPlanModuleCreate,
    EducationPlanModuleUpdate,
    EducationPlanModulePatch,
    EducationPlanModuleReorder
)


class EducationPlanModuleService:

    def __init__(
            self,
            repo: EducationPlanModuleRepository,
            plan_repo: EducationPlanRepository,
            module_repo: ModuleRepository
    ):
        self.repo = repo
        self.plan_repo = plan_repo
        self.module_repo = module_repo


    # проверить план и модуль
    async def _validate(self, plan_id: int, module_id: int):
        plan = await self.plan_repo.get_by_id(plan_id)

        if not plan:
            raise ValueError("Education plan not found")

        module = await self.module_repo.get_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        return plan, module


    # добавить модуль
    async def add_module(self, data: EducationPlanModuleCreate):
        await self._validate(data.education_plan_id, data.module_id)
        existing = await self.repo.get_by_plan_and_module(
            data.education_plan_id,data.module_id)

        if existing:
            raise ValueError("Module already exists in plan")

        return await self.repo.create(
            data.education_plan_id,
            data.module_id,
            data.order_number
        )


    # удалить модуль
    async def remove_module(self, plan_id: int, module_id: int):
        link = await self.repo.get_by_plan_and_module(plan_id, module_id)

        if not link:
            raise ValueError("Module not found in plan")

        return await self.repo.delete(link.id)


    # получить модули плана
    async def get_plan_modules(self, plan_id: int):
        await self.plan_repo.get_by_id(plan_id)
        modules = await self.repo.get_modules_by_plan(plan_id)

        return sorted(modules, key=lambda x: x.order_number)


    # изменить порядок одного модуля
    async def update_module_order(self, plan_id: int, module_id: int, new_order: int):
        link = await self.repo.get_by_plan_and_module(plan_id, module_id)

        if not link:
            raise ValueError("Module not found in plan")

        link.order_number = new_order

        return await self.repo.update(
            link.id,
            {
                "order_number": link.order_number
            }
        )


    # update (полное обновление)
    async def update(self, plan_id: int, module_id: int, data: EducationPlanModuleUpdate):
        link = await self.repo.get_by_plan_and_module(plan_id, module_id)

        if not link:
            raise ValueError("Module not found in plan")

        if data.education_plan_id is not None:
            link.education_plan_id = data.education_plan_id

        if data.module_id is not None:
            link.module_id = data.module_id

        if data.order_number is not None:
            link.order_number = data.order_number

        return await self.repo.update(
            link.id,
            {
                "education_plan_id": link.education_plan_id,
                "module_id": link.module_id,
                "order_number": link.order_number
            }
        )


    # patch (частичное обновление)
    async def patch(self, plan_id: int, module_id: int, data: EducationPlanModulePatch):
        link = await self.repo.get_by_plan_and_module(plan_id, module_id)

        if not link:
            raise ValueError("Module not found in plan")

        if data.order_number is not None:
            link.order_number = data.order_number

        return await self.repo.update(
            link.id,
            {
                "order_number": link.order_number
            }
        )


    # полный reorder
    async def reorder_plan(self, plan_id: int, data: EducationPlanModuleReorder):
        await self.plan_repo.get_by_id(plan_id)

        for item in data.modules:
            link = await self.repo.get_by_plan_and_module(plan_id,item["module_id"])

            if not link:
                raise ValueError(f"Module {item['module_id']} not found")

            link.order_number = item["order_number"]
            await self.repo.update(
                link.id,
                {
                    "order_number": link.order_number
                }
            )

        return await self.get_plan_modules(plan_id)


    # проверка существует ли модуль
    async def check_exists(self, plan_id: int, module_id: int):
        link = await self.repo.get_by_plan_and_module(plan_id, module_id)

        return link is not None


    # массовое добавление
    async def bulk_add_modules(self, plan_id: int, modules: list[dict]):
        await self.plan_repo.get_by_id(plan_id)
        results = []

        for item in modules:
            exists = await self.repo.get_by_plan_and_module(plan_id,item["module_id"])

            if exists:
                continue

            await self.module_repo.get_by_id(item["module_id"])
            created = await self.repo.create(
                plan_id=plan_id,
                module_id=item["module_id"],
                order_number=item["order_number"])

            results.append(created)

        return results


    # очистить план
    async def clear_plan(self, plan_id: int):
        await self.plan_repo.get_by_id(plan_id)

        return await self.repo.delete_by_plan_id(plan_id)


    # количество модулей
    async def count_modules(self, plan_id: int):
        modules = await self.repo.get_modules_by_plan(plan_id)

        return len(modules)


    # заменить полностью список модулей
    async def replace_modules(self, plan_id: int, modules: list[dict]):
        await self.plan_repo.get_by_id(plan_id)
        await self.repo.delete_by_plan_id(plan_id)

        for item in modules:
            await self.repo.create(
                plan_id=plan_id,
                module_id=item["module_id"],
                order_number=item["order_number"])

        return await self.get_plan_modules(plan_id)