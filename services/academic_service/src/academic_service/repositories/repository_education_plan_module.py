from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from academic_service.models.models_education_plan_modules import EducationPlanModule



class EducationPlanModuleRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    # Добавить модуль в учебный план
    # async def create(self,item: EducationPlanModule):
    #     self.db.add(item)
    #     await self.db.commit()
    #     await self.db.refresh(item)
    #
    #     return item

    async def create(self,plan_id: int,module_id: int,order_number: int):
        item = EducationPlanModule(education_plan_id=plan_id, module_id=module_id,order_number=order_number)
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)

        return item



    # Получить связь по id
    async def get_by_id(self,item_id: int):
        result = await self.db.execute(select(EducationPlanModule).where(EducationPlanModule.id == item_id))

        return result.scalar_one_or_none()


    # Все связи
    async def get_all(self):
        result = await self.db.execute(select(EducationPlanModule).order_by(EducationPlanModule.order_number))

        return result.scalars().all()


    # Все модули конкретного плана
    async def get_by_plan(self,education_plan_id: int):
        result = await self.db.execute(select(EducationPlanModule)
            .where(EducationPlanModule.education_plan_id ==education_plan_id)
            .order_by(EducationPlanModule.order_number))

        return result.scalars().all()


    # Все планы. где используется модуль
    async def get_by_module(self,module_id: int):
        result = await self.db.execute(select(EducationPlanModule)
            .where(EducationPlanModule.module_id ==module_id))

        return result.scalars().all()


    # Проверка существует ли модуль в плане
    async def exists(self, education_plan_id: int,module_id: int):
        result = await self.db.execute(select(EducationPlanModule.id)
            .where(EducationPlanModule.education_plan_id ==
                education_plan_id,EducationPlanModule.module_id ==module_id))

        return result.scalar_one_or_none() is not None


    # Добавить модуль если его нет
    async def add_if_not_exists(self,item: EducationPlanModule):
        exists = await self.exists(item.education_plan_id,item.module_id)

        if exists:
            return None

        return await self.create(
            item.education_plan_id,
            item.module_id,
            item.order_number
        )


    # Изменить порядок
    async def update_order(self,item_id: int,order_number: int):
        await self.db.execute(update(EducationPlanModule).where(EducationPlanModule.id == item_id).values(order_number=order_number))
        await self.db.commit()

        return await self.get_by_id(item_id)


    # Переместить модуль в другой план
    async def move_to_plan(self, item_id: int,new_plan_id: int):
        await self.db.execute(update(EducationPlanModule)
            .where(EducationPlanModule.id == item_id).values(education_plan_id=new_plan_id))
        await self.db.commit()

        return await self.get_by_id(item_id)


    # Обновление связи
    async def update(self, item_id: int,data: dict):
        await self.db.execute(update(EducationPlanModule)
            .where(EducationPlanModule.id == item_id).values(**data))

        await self.db.commit()

        return await self.get_by_id(item_id)


    # Удалить модуль из плана
    async def delete(self,item_id: int):
        await self.db.execute(delete(EducationPlanModule).where(EducationPlanModule.id == item_id))

        await self.db.commit()

    # Удалить все модули учебного плана
    async def delete_by_plan_id(self, plan_id: int):
        await self.db.execute(
            delete(EducationPlanModule)
            .where(EducationPlanModule.education_plan_id == plan_id)
        )

        await self.db.commit()

    # -------------------------------------------------------------

    async def is_plan_used(self, plan_id: int):
        result = await self.db.execute(
            select(EducationPlanModule)
            .where(
                EducationPlanModule.education_plan_id == plan_id
            )
        )

        return result.scalar_one_or_none() is not None

    async def get_modules_by_plan(self, plan_id: int):
        result = await self.db.execute(
            select(EducationPlanModule)
            .where(
                EducationPlanModule.education_plan_id == plan_id
            )
            .order_by(
                EducationPlanModule.order_number
            )
        )

        return result.scalars().all()

    async def get_by_plan_and_module(
            self,
            plan_id: int,
            module_id: int
    ):
        result = await self.db.execute(
            select(EducationPlanModule)
            .where(
                EducationPlanModule.education_plan_id == plan_id,
                EducationPlanModule.module_id == module_id
            )
        )

        return result.scalar_one_or_none()