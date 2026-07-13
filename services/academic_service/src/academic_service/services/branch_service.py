from academic_service.repositories.branch_repository import BranchRepository
from academic_service.repositories.branch_address_repository import BranchAddressRepository
from academic_service.schemas.branch import (
    BranchCreate,
    BranchUpdate,
    BranchPatch,
    BranchShortResponse,
    BranchClose,
    BranchActivate,
    BranchFilter
)
from academic_service.schemas.branch_address import (BranchAddressCreate, BranchAddressUpdate)


class BranchService:

    def __init__(self, branch_repo: BranchRepository, address_repo: BranchAddressRepository):
        self.branch_repo = branch_repo
        self.address_repo = address_repo

    # создать филиал + адрес
    async def create_branch(self, data: BranchCreate):
        existing = await self.branch_repo.get_by_email(data.email)

        if existing:
            raise ValueError("Branch already exists")

        branch = await self.branch_repo.create(data)

        return branch

    # получить филиал
    async def get_branch(self, branch_id: int):
        branch = await self.branch_repo.get_by_id(branch_id)

        if not branch:
            raise ValueError("Branch not found")

        return branch

    # список филиалов
    async def get_branches(self, active_only: bool = True):

        if active_only:
            return await self.branch_repo.get_active()

        return await self.branch_repo.get_all()

    # обновление
    async def update_branch(self, branch_id: int, data: BranchUpdate):
        branch = await self.get_branch(branch_id)

        if data.branch_address_id is not None:
            address = await self.address_repo.get_by_id(data.branch_address_id)
            if not address:
                raise ValueError("Address not found")
            branch.branch_address_id = data.branch_address_id

        if data.phone is not None:
            branch.phone = data.phone

        if data.email is not None:
            branch.email = data.email

        return await self.branch_repo.update(branch)

    # patch
    async def patch_branch(self, branch_id: int, data: BranchPatch):
        branch = await self.get_branch(branch_id)

        if data.phone is not None:
            branch.phone = data.phone

        if data.email is not None:
            branch.email = data.email

        if data.branch_address_id is not None:
            branch.branch_address_id = data.branch_address_id

        if data.is_active is not None:
            branch.is_active = data.is_active

        return await self.branch_repo.update(branch)

    # удалить
    async def delete_branch(self, branch_id: int):
        branch = await self.get_branch(branch_id)

        return await self.branch_repo.delete(branch_id)

    # -------------------------------------------------------

    # получить филиал + адрес
    async def get_branch_detail(self, branch_id: int):
        branch = await self.get_branch(branch_id)
        address = await self.address_repo.get_by_id(branch.branch_address_id)

        return {"branch": branch, "address": address}

    # фильтр филиалов
    async def filter_branches(self, data: BranchFilter):

        return await self.branch_repo.filter(
            city=data.city,
            country=data.country,
            is_active=data.is_active)

    # поиск по городу
    async def get_by_city(self, city: str):
        addresses = await self.address_repo.get_by_city(city)
        result = []

        for address in addresses:
            branch = await self.branch_repo.get_by_address_id(address.id)

            if branch:
                result.append(branch)

        return result

    # закрыть филиал
    async def close_branch(self, branch_id: int, data: BranchClose):
        branch = await self.get_branch(branch_id)
        branch.is_active = False
        branch.closed_at = data.closed_at

        return await self.branch_repo.update(branch)

    # открыть филиал
    async def activate_branch(self, branch_id: int, data: BranchActivate):
        branch = await self.get_branch(branch_id)
        branch.is_active = data.is_active
        branch.closed_at = None

        return await self.branch_repo.update(branch)

    # безопасное удаление с адресом
    async def safe_delete_branch(self, branch_id: int):
        branch = await self.get_branch(branch_id)
        await self.branch_repo.delete(branch.id)
        await self.address_repo.delete(branch.branch_address_id)

        return True

    # получить адрес
    async def get_address(self, branch_id: int):
        branch = await self.get_branch(branch_id)

        return await self.address_repo.get_by_id(branch.branch_address_id)

    # изменить адрес
    async def update_address(self, branch_id: int, data: BranchAddressUpdate):
        address = await self.get_address(branch_id)

        return await self.address_repo.update(address, data)

    # существует ли
    async def exists(self, branch_id: int):
        branch = await self.branch_repo.get_by_id(branch_id)

        return branch is not None

    # количество активных
    async def count_active(self):
        branches = await self.branch_repo.get_active()

        return len(branches)

    # короткий список
    async def get_short_list(self):
        branches = await self.branch_repo.get_active()
        result = []

        for branch in branches:
            address = await self.get_address(branch.id)
            result.append(
                BranchShortResponse(
                    id=branch.id,
                    city=address.city,
                    street=address.street,
                    house=address.house))

        return result
