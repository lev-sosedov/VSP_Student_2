from academic_service.repositories.group_repository import GroupRepository


class GroupService:


    def __init__(
        self,
        repo: GroupRepository
    ):
        self.repo = repo



    async def create_group(self, data):

        # бизнес правила

        if not data.name:
            raise ValueError(
                "Group name required"
            )


        group = Group(
            name=data.name,
            direction_id=data.direction_id,
            branch_id=data.branch_id
        )


        return await self.repo.create(group)