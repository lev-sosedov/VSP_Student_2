from academic_service.repositories.group_repository import GroupRepository
from academic_service.repositories.branch_repository import BranchRepository
from academic_service.repositories.direction_repository import DirectionRepository
from academic_service.repositories.education_plan_repository import EducationPlanRepository

from academic_service.schemas.group import GroupCreate, GroupUpdate, GroupPatch



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
    async def create_group(
        self,
        data: GroupCreate
    ):


        branch = await self.branch_repo.get_by_id(
            data.branch_id
        )


        if not branch:

            raise ValueError(
                "Branch not found"
            )



        direction = await self.direction_repo.get_by_id(
            data.direction_id
        )


        if not direction:

            raise ValueError(
                "Direction not found"
            )



        plan = await self.plan_repo.get_by_id(
            data.education_plan_id
        )


        if not plan:

            raise ValueError(
                "Education plan not found"
            )



        existing = await self.repo.get_by_name(
            data.name
        )


        if existing:

            raise ValueError(
                "Group already exists"
            )



        return await self.repo.create(data)



    # получить группу
    async def get_group(
        self,
        group_id: int
    ):


        group = await self.repo.get_by_id(
            group_id
        )


        if not group:

            raise ValueError(
                "Group not found"
            )


        return group



    # список групп
    async def get_groups(
        self,
        limit: int = 20,
        offset: int = 0
    ):

        return await self.repo.get_all(
            limit,
            offset
        )



    # группы филиала
    async def get_branch_groups(
        self,
        branch_id: int
    ):

        return await self.repo.get_by_branch(
            branch_id
        )



    # группы направления
    async def get_direction_groups(
        self,
        direction_id: int
    ):

        return await self.repo.get_by_direction(
            direction_id
        )



    # обновление группы
    async def update_group(
        self,
        group_id: int,
        data: GroupUpdate
    ):


        group = await self.repo.get_by_id(
            group_id
        )


        if not group:

            raise ValueError(
                "Group not found"
            )



        if data.name is not None:

            group.name = data.name



        if data.start_date is not None:

            group.start_date = data.start_date



        if data.end_date is not None:

            group.end_date = data.end_date



        return await self.repo.update(
            group
        )



    # patch обновление
    async def patch_group(
        self,
        group_id: int,
        data: GroupPatch
    ):


        group = await self.repo.get_by_id(
            group_id
        )


        if not group:

            raise ValueError(
                "Group not found"
            )



        if data.name is not None:

            group.name = data.name



        if data.is_active is not None:

            group.is_active = data.is_active



        if data.closed_at is not None:

            group.closed_at = data.closed_at



        return await self.repo.update(
            group
        )



    # закрыть группу
    async def close_group(
        self,
        group_id: int
    ):


        group = await self.repo.get_by_id(
            group_id
        )


        if not group:

            raise ValueError(
                "Group not found"
            )


        group.is_active = False


        return await self.repo.update(
            group
        )



    # открыть группу
    async def activate_group(
        self,
        group_id: int
    ):


        group = await self.repo.get_by_id(
            group_id
        )


        if not group:

            raise ValueError(
                "Group not found"
            )


        group.is_active = True


        return await self.repo.update(
            group
        )



    # удалить группу
    async def delete_group(
        self,
        group_id: int
    ):


        group = await self.repo.get_by_id(
            group_id
        )


        if not group:

            raise ValueError(
                "Group not found"
            )


        return await self.repo.delete(
            group_id
        )



    # получить полную информацию о группе
    async def get_group_details(
        self,
        group_id: int
    ):


        group = await self.repo.get_by_id(
            group_id
        )


        if not group:

            raise ValueError(
                "Group not found"
            )


        return {

            "group": group,

            "branch": group.branch,

            "direction": group.direction,

            "education_plan": group.education_plan

        }



    # проверка можно ли добавить студентов
    async def can_accept_students(
        self,
        group_id: int
    ):


        group = await self.repo.get_by_id(
            group_id
        )


        if not group:

            return False



        return group.is_active