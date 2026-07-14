from academic_service.repositories.repository_group import GroupRepository
from academic_service.repositories.repository_branch import BranchRepository
from academic_service.repositories.repository_direction import DirectionRepository
from academic_service.repositories.repository_education_plan import EducationPlanRepository
from academic_service.models.models_group import Group
from academic_service.schemas.schemas_group import GroupCreate, GroupUpdate, GroupPatch



class GroupService:


    def __init__(
        self,
        repo: GroupRepository,
        branch_repo: BranchRepository,
        direction_repo: DirectionRepository,
        plan_repo: EducationPlanRepository
    ):
        self.repo = repo
        self.branch_repo = branch_repo
        self.direction_repo = direction_repo
        self.plan_repo = plan_repo



    # создание группы
    async def create_group(self,data: GroupCreate):
        branch = await self.branch_repo.get_by_id(data.branch_id)

        if not branch:
            raise ValueError("Branch not found")

        direction = await self.direction_repo.get_by_id(data.direction_id)

        if not direction:
            raise ValueError("Direction not found")

        plan = await self.plan_repo.get_by_id(data.education_plan_id)

        if not plan:
            raise ValueError("Education plan not found")

        existing = await self.repo.get_by_name(data.name)

        if existing:
            raise ValueError("Group already exists")

        group = Group(
            name=data.name,
            branch_id=data.branch_id,
            direction_id=data.direction_id,
            education_plan_id=data.education_plan_id,
            start_date=data.start_date,
            end_date=data.end_date
        )

        return await self.repo.create(group)



    # получить группу
    async def get_group(self,group_id: int):
        group = await self.repo.get_by_id(group_id)

        if not group:
            raise ValueError("Group not found")

        return group


    # список групп
    async def get_groups(self,limit: int = 20,offset: int = 0):

        return await self.repo.get_all(limit,offset)


    # группы филиала
    async def get_branch_groups(self,branch_id: int):

        return await self.repo.get_by_branch(branch_id)


    # группы направления
    async def get_direction_groups(self,direction_id: int):

        return await self.repo.get_by_direction(direction_id)


    # обновление группы
    # async def update_group(self,group_id: int,data: GroupUpdate):
    #
    #     group = await self.repo.get_by_id(group_id)
    #
    #     if not group:
    #         raise ValueError("Group not found")
    #
    #     if data.name is not None:
    #         group.name = data.name
    #
    #     if data.start_date is not None:
    #         group.start_date = data.start_date
    #
    #     if data.end_date is not None:
    #         group.end_date = data.end_date
    #
    #     return await self.repo.update(group)

    # обновление группы
    async def update_group(
            self,
            group_id: int,
            data: GroupUpdate
    ):

        group = await self.repo.get_by_id(group_id)

        if not group:
            raise ValueError("Group not found")

        update_data = {}

        if data.name is not None:
            update_data["name"] = data.name

        if data.branch_id is not None:
            update_data["branch_id"] = data.branch_id

        if data.direction_id is not None:
            update_data["direction_id"] = data.direction_id

        if data.education_plan_id is not None:
            update_data["education_plan_id"] = data.education_plan_id

        if data.start_date is not None:
            update_data["start_date"] = data.start_date

        if data.end_date is not None:
            update_data["end_date"] = data.end_date

        return await self.repo.update(
            group_id,
            update_data
        )



    # patch обновление
    # async def patch_group(self,group_id: int,data: GroupPatch):
    #     group = await self.repo.get_by_id(group_id)
    #
    #     if not group:
    #         raise ValueError("Group not found")
    #
    #     if data.name is not None:
    #         group.name = data.name
    #
    #     return await self.repo.update(group)

    # PATCH обновление
    async def patch_group(
            self,
            group_id: int,
            data: GroupPatch
    ):

        group = await self.repo.get_by_id(group_id)

        if not group:
            raise ValueError("Group not found")

        patch_data = {}

        if data.name is not None:
            patch_data["name"] = data.name

        if data.branch_id is not None:
            patch_data["branch_id"] = data.branch_id

        if data.direction_id is not None:
            patch_data["direction_id"] = data.direction_id

        if data.education_plan_id is not None:
            patch_data["education_plan_id"] = data.education_plan_id

        if data.start_date is not None:
            patch_data["start_date"] = data.start_date

        if data.end_date is not None:
            patch_data["end_date"] = data.end_date

        return await self.repo.update(
            group_id,
            patch_data
        )




    # закрыть группу
    # async def close_group(self,group_id: int):
    #     group = await self.repo.get_by_id(group_id)
    #
    #     if not group:
    #         raise ValueError("Group not found")
    #
    #     group.is_active = False
    #
    #     return await self.repo.update(group)

    async def close_group(
            self,
            group_id: int
    ):

        group = await self.repo.get_by_id(group_id)

        if not group:
            raise ValueError("Group not found")

        return await self.repo.update(
            group_id,
            {
                "is_active": False
            }
        )




    # открыть группу
    # async def activate_group(self,group_id: int):
    #     group = await self.repo.get_by_id(group_id)
    #
    #     if not group:
    #         raise ValueError("Group not found")
    #
    #     group.is_active = True
    #
    #     return await self.repo.update(group)

    async def activate_group(
            self,
            group_id: int
    ):

        group = await self.repo.get_by_id(group_id)

        if not group:
            raise ValueError("Group not found")

        return await self.repo.update(
            group_id,
            {
                "is_active": True
            }
        )



    # удалить группу
    async def delete_group(self,group_id: int):
        group = await self.repo.get_by_id(group_id)

        if not group:
            raise ValueError("Group not found")

        return await self.repo.delete(group_id)



    # получить полную информацию о группе
    async def get_group_details(self,group_id: int):
        group = await self.repo.get_by_id(group_id)

        if not group:
            raise ValueError("Group not found")

        return {"group": group,
            "branch": group.branch,
            "direction": group.direction,
            "education_plan": group.education_plan}



    # проверка можно ли добавить студентов
    async def can_accept_students(self,group_id: int):
        group = await self.repo.get_by_id(group_id)

        if not group:
            return False

        return group.is_active

    # получить активные группы
    async def get_active_groups(self):

        return await self.repo.get_active()

    # получить закрытые группы
    async def get_closed_groups(self):

        return await self.repo.get_closed()

    # восстановить группу
    async def restore_group(
            self,
            group_id: int
    ):

        group = await self.repo.get_by_id(group_id)

        if not group:
            raise ValueError(
                "Group not found"
            )

        return await self.repo.activate(group_id)

    # безопасное удаление группы
    async def safe_delete_group(
            self,
            group_id: int
    ):

        group = await self.repo.get_by_id(group_id)

        if not group:
            raise ValueError(
                "Group not found"
            )

        return await self.repo.delete(group_id)

    # проверка существования группы
    async def exists(
            self,
            group_id: int
    ):

        return await self.repo.exists(group_id)

    # поиск групп
    async def search(
            self,
            name: str
    ):

        return await self.repo.search_by_name(name)

    # группы филиала
    async def get_by_branch(
            self,
            branch_id: int
    ):

        return await self.repo.get_by_branch(branch_id)

    # группы направления
    async def get_by_direction(
            self,
            direction_id: int
    ):

        return await self.repo.get_by_direction(direction_id)

    # группы учебного плана
    async def get_by_plan(
            self,
            education_plan_id: int
    ):

        return await self.repo.get_by_plan(
            education_plan_id
        )