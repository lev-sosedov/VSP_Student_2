from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_chat_member_role import (
    ChatMemberRole
)

from communication_service.messaging.messaging_rpc_client import communication_rpc_client
from communication_service.models.model_chat_member import (
    ChatMember
)
from communication_service.repositories.repository_chat import (
    ChatRepository
)
from communication_service.repositories.repository_chat_member import (
    ChatMemberRepository
)
from communication_service.schemas.schemas_chat_member import (
    ChatMemberCreate,
    ChatMemberRoleUpdate
)
from communication_service.services.service_external_validation import (
    external_validation_service
)
from common.utils.enum_chat_type import ChatType


class ChatMemberService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.chat_repository = ChatRepository(
            session=session
        )

        self.member_repository = (
            ChatMemberRepository(
                session=session
            )
        )

    # =================================================
    # Получить участника по ID
    # =================================================

    async def get_by_id(
        self,
        member_id: int
    ) -> ChatMember | None:
        return await self.member_repository.get_by_id(
            member_id=member_id
        )

    # =================================================
    # Получить список участников
    # =================================================

    async def get_list(
        self,
        chat_id: int,
        is_active: bool | None = None,
        member_role: ChatMemberRole | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[ChatMember], int]:
        chat = await self.chat_repository.get_by_id(
            chat_id=chat_id
        )

        if chat is None:
            raise ValueError(
                "Чат не найден"
            )

        return await self.member_repository.get_list(
            chat_id=chat_id,
            is_active=is_active,
            member_role=member_role,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Добавить участника
    # =================================================

    async def create(
            self,
            member_data: ChatMemberCreate
    ) -> ChatMember:
        chat = await self.chat_repository.get_by_id(
            chat_id=member_data.chat_id
        )

        if chat is None:
            raise ValueError(
                "Чат не найден"
            )

        if not chat.is_active:
            raise ValueError(
                "Нельзя добавлять участников "
                "в неактивный чат"
            )

        await external_validation_service.get_active_user(
            user_id=member_data.user_id
        )

        await external_validation_service.get_active_user(
            user_id=member_data.added_by
        )

        if (
                chat.chat_type == ChatType.GROUP
                and chat.group_id is not None
        ):
            response = await (
                communication_rpc_client.call_academic(
                    method="group_member.exists",
                    payload={
                        "group_id": chat.group_id,
                        "user_id": member_data.user_id
                    }
                )
            )

            if not response.get("success"):
                raise ValueError(
                    response.get(
                        "error",
                        "Ошибка Academic Service"
                    )
                )

            if not response.get("is_member"):
                raise ValueError(
                    "Пользователь не состоит "
                    "в учебной группе этого чата"
                )

        await self._validate_add_access(
            chat_id=chat.id,
            requested_by=member_data.added_by,
            new_role=member_data.member_role
        )

        existing_member = (
            await self.member_repository.get_member(
                chat_id=chat.id,
                user_id=member_data.user_id
            )
        )

        if existing_member is not None:
            if existing_member.is_active:
                raise ValueError(
                    "Пользователь уже состоит в чате"
                )

            return await self.member_repository.reactivate(
                member=existing_member,
                member_role=member_data.member_role,
                added_by=member_data.added_by
            )

        return await self.member_repository.create(
            chat_id=member_data.chat_id,
            user_id=member_data.user_id,
            member_role=member_data.member_role,
            added_by=member_data.added_by
        )

    # =================================================
    # Изменить роль
    # =================================================

    async def update_role(
        self,
        member: ChatMember,
        role_data: ChatMemberRoleUpdate
    ) -> ChatMember:
        if not member.is_active:
            raise ValueError(
                "Нельзя изменить роль "
                "неактивного участника"
            )

        requester = await self._get_active_member(
            chat_id=member.chat_id,
            user_id=role_data.changed_by
        )

        if member.member_role == ChatMemberRole.OWNER:
            raise ValueError(
                "Нельзя изменить роль владельца чата"
            )

        if role_data.member_role == ChatMemberRole.OWNER:
            raise ValueError(
                "Передача владения чатам пока "
                "не поддерживается"
            )

        if (
            role_data.member_role
            == ChatMemberRole.ADMIN
            and requester.member_role
            != ChatMemberRole.OWNER
        ):
            raise ValueError(
                "Назначить администратора "
                "может только владелец чата"
            )

        if requester.member_role not in {
            ChatMemberRole.OWNER,
            ChatMemberRole.ADMIN
        }:
            raise ValueError(
                "Недостаточно прав для изменения роли"
            )

        if (
            requester.member_role
            == ChatMemberRole.ADMIN
            and member.member_role
            == ChatMemberRole.ADMIN
        ):
            raise ValueError(
                "Администратор не может менять "
                "роль другого администратора"
            )

        return await self.member_repository.set_role(
            member=member,
            member_role=role_data.member_role
        )

    # =================================================
    # Деактивировать участника
    # =================================================

    async def deactivate(
        self,
        member: ChatMember,
        requested_by: int
    ) -> ChatMember:
        if not member.is_active:
            raise ValueError(
                "Участник уже неактивен"
            )

        if member.member_role == ChatMemberRole.OWNER:
            raise ValueError(
                "Нельзя удалить владельца чата"
            )

        requester = await self._get_active_member(
            chat_id=member.chat_id,
            user_id=requested_by
        )

        if requester.member_role not in {
            ChatMemberRole.OWNER,
            ChatMemberRole.ADMIN
        }:
            raise ValueError(
                "Недостаточно прав для удаления участника"
            )

        if (
            requester.member_role
            == ChatMemberRole.ADMIN
            and member.member_role
            == ChatMemberRole.ADMIN
        ):
            raise ValueError(
                "Администратор не может удалить "
                "другого администратора"
            )

        return await self.member_repository.deactivate(
            member=member
        )

    # =================================================
    # Активировать участника
    # =================================================

    async def activate(
        self,
        member: ChatMember,
        requested_by: int
    ) -> ChatMember:
        if member.is_active:
            raise ValueError(
                "Участник уже активен"
            )

        requester = await self._get_active_member(
            chat_id=member.chat_id,
            user_id=requested_by
        )

        if requester.member_role not in {
            ChatMemberRole.OWNER,
            ChatMemberRole.ADMIN
        }:
            raise ValueError(
                "Недостаточно прав для возврата участника"
            )

        return await self.member_repository.activate(
            member=member
        )

    # =================================================
    # Покинуть чат
    # =================================================

    async def leave(
        self,
        chat_id: int,
        user_id: int
    ) -> ChatMember:
        member = await self.member_repository.get_member(
            chat_id=chat_id,
            user_id=user_id
        )

        if member is None or not member.is_active:
            raise ValueError(
                "Пользователь не состоит в чате"
            )

        if member.member_role == ChatMemberRole.OWNER:
            raise ValueError(
                "Владелец не может покинуть чат. "
                "Сначала нужно передать владение "
                "или закрыть чат"
            )

        return await self.member_repository.deactivate(
            member=member
        )

    # =================================================
    # Проверка права добавления
    # =================================================

    async def _validate_add_access(
        self,
        chat_id: int,
        requested_by: int,
        new_role: ChatMemberRole
    ) -> None:
        requester = await self._get_active_member(
            chat_id=chat_id,
            user_id=requested_by
        )

        if requester.member_role not in {
            ChatMemberRole.OWNER,
            ChatMemberRole.ADMIN
        }:
            raise ValueError(
                "Недостаточно прав для добавления участника"
            )

        if (
            new_role == ChatMemberRole.OWNER
        ):
            raise ValueError(
                "Нельзя добавить второго владельца чата"
            )

        if (
            new_role == ChatMemberRole.ADMIN
            and requester.member_role
            != ChatMemberRole.OWNER
        ):
            raise ValueError(
                "Добавить администратора "
                "может только владелец"
            )

    # =================================================
    # Получить активного участника
    # =================================================

    async def _get_active_member(
        self,
        chat_id: int,
        user_id: int
    ) -> ChatMember:
        member = await self.member_repository.get_member(
            chat_id=chat_id,
            user_id=user_id
        )

        if member is None or not member.is_active:
            raise ValueError(
                "Пользователь не является "
                "активным участником чата"
            )

        return member