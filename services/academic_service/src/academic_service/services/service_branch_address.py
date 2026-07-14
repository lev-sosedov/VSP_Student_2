from academic_service.repositories.repository_branch_address import BranchAddressRepository

from academic_service.schemas.schemas_branch_address import (
    BranchAddressCreate,
    BranchAddressUpdate,
    BranchAddressPatch,
    BranchAddressShortResponse
)


class BranchAddressService:

    def __init__(self, repo: BranchAddressRepository):
        self.repo = repo

    # создать адрес
    async def create_address(self, data: BranchAddressCreate):
        return await self.repo.create(data)

    # получить по id
    async def get_address(self, address_id: int):
        address = await self.repo.get_by_id(address_id)

        if not address:
            raise ValueError("Address not found")

        return address

    # получить все адреса
    async def get_addresses(self, limit: int = 20, offset: int = 0):
        return await self.repo.get_all(limit=limit, offset=offset)

    # обновить полностью
    async def update_address(self, address_id: int, data: BranchAddressUpdate):
        address = await self.repo.get_by_id(address_id)

        if not address:
            raise ValueError("Address not found")

        return await self.repo.update(address, data)

    # частичное обновление
    async def patch_address(self, address_id: int, data: BranchAddressPatch, ):
        address = await self.repo.get_by_id(address_id)

        if not address:
            raise ValueError("Address not found")

        return await self.repo.patch(address, data)

    # удалить адрес
    async def delete_address(self, address_id: int):
        address = await self.repo.get_by_id(address_id)

        if not address:
            raise ValueError("Address not found")

        return await self.repo.delete(address_id)

    # -------------------------------------------------------------------------------------

    # получить по стране
    async def get_by_country(self, country: str):
        return await self.repo.get_by_country(country)

    # получить по городу
    async def get_by_city(self, city: str):
        return await self.repo.get_by_city(city)

    # получить по улице
    async def get_by_street(self, street: str):
        return await self.repo.search(street)

    # поиск (универсальный)
    async def search(self, query: str):
        return await self.repo.search(query)

    # фильтрованный поиск (максимально полезный для API)
    async def filter_addresses(self, country: str | None = None, city: str | None = None, street: str | None = None):
        return await self.repo.filter(country=country, city=city, street=street)

    # безопасное удаление (проверка использования)
    async def safe_delete_address(self, address_id: int, branch_repo=None):
        address = await self.repo.get_by_id(address_id)

        if not address:
            raise ValueError("Address not found")

        # если передан branch_repo — проверяем использование
        if branch_repo:
            used = await branch_repo.get_by_address_id(address_id)

            if used:
                raise ValueError("Address is used by branch and cannot be deleted")

        return await self.repo.delete(address_id)

    # проверить существование
    async def exists(self, address_id: int):
        address = await self.repo.get_by_id(address_id)

        return address is not None

    # форматированный адрес (для UI / API)
    async def get_full_address(self, address_id: int):
        address = await self.get_address(address_id)

        result = f"{address.country}, {address.city}, ул. {address.street}, дом {address.house}"

        if address.building:
            result += f", корпус {address.building}"

        if address.postal_code:
            result += f", {address.postal_code}"

        return result

    # короткий формат (для списков)
    async def get_short(self, address_id: int):
        address = await self.get_address(address_id)

        return BranchAddressShortResponse(
            id=address.id,
            country=address.country,
            city=address.city,
            street=address.street,
            house=address.house
        )

    # массовое создание адресов (для импорта / админки)
    async def bulk_create(self, addresses: list[BranchAddressCreate]):
        result = []

        for addr in addresses:
            created = await self.repo.create(addr)
            result.append(created)

        return result

    # количество адресов
    async def count(self):
        return len(await self.repo.get_all())
