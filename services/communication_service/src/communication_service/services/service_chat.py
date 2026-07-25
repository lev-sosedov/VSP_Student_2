from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_chat_member_role import (
    ChatMemberRole
)
from common.utils.enum_chat_type import ChatType
from common.utils.enum_message_type import MessageType
from communication_service.models.model_chat import (
    Chat
)
from communication_service.repositories.repository_chat import (
    ChatRepository
)
from communication_service.repositories.repository_chat_member import (
    ChatMemberRepository
)
from communication_service.repositories.repository_message import (
    MessageRepository
)
from communication_service.schemas.schemas_chat import (
    ChatCreate,
    ChatUpdate
)
from communication_service.services.service_external_validation import (
    external_validation_service
)


class ChatService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

        self.chat_repository = ChatRepository(
            session=session
        )

        self.member_repository = (
            ChatMemberRepository(
                session=session
            )
        )

        self.message_repository = MessageRepository(
            session=session
        )

    # =================================================
    # Получить чат
    # =================================================

    async def get_by_id(
        self,
        chat_id: int,
        with_members: bool = False
    ) -> Chat | None:
        return await self.chat_repository.get_by_id(
            chat_id=chat_id,
            with_members=with_members
        )

    # =================================================
    # Список чатов
    # =================================================

    async def get_list(
        self,
        chat_type: ChatType | None = None,
        group_id: int | None = None,
        lesson_id: int | None = None,
        created_by: int | None = None,
        is_active: bool | None = None,
        is_archived: bool | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[Chat], int]:
        return await self.chat_repository.get_list(
            chat_type=chat_type,
            group_id=group_id,
            lesson_id=lesson_id,
            created_by=created_by,
            is_active=is_active,
            is_archived=is_archived,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Создать чат
    # =================================================

    async def create(
        self,
        chat_data: ChatCreate
    ) -> Chat:
        # Проверяем создателя через user-service
        await external_validation_service.get_active_user(
            user_id=chat_data.created_by
        )

        # =============================================
        # Групповой чат
        # =============================================

        if chat_data.chat_type == ChatType.GROUP:
            if chat_data.group_id is None:
                raise ValueError(
                    "Для группового чата нужен group_id"
                )

            await external_validation_service.get_group(
                group_id=chat_data.group_id
            )

            existing_chat = (
                await self.chat_repository.get_group_chat(
                    group_id=chat_data.group_id
                )
            )

            if existing_chat is not None:
                raise ValueError(
                    "Активный чат этой группы уже существует"
                )

        # =============================================
        # Чат занятия
        # =============================================

        if chat_data.chat_type == ChatType.LESSON:
            if chat_data.lesson_id is None:
                raise ValueError(
                    "Для чата занятия нужен lesson_id"
                )

            lesson = await external_validation_service.get_lesson(
                lesson_id=chat_data.lesson_id
            )

            existing_chat = (
                await self.chat_repository.get_lesson_chat(
                    lesson_id=chat_data.lesson_id
                )
            )

            if existing_chat is not None:
                raise ValueError(
                    "Активный чат этого занятия уже существует"
                )

            # group_id для чата занятия берём
            # из самого занятия
            if chat_data.group_id is None:
                chat_data.group_id = lesson.get(
                    "group_id"
                )

        create_data = chat_data.model_dump()

        chat = await self.chat_repository.create(
            chat_data=create_data
        )

        # Создатель всегда становится владельцем
        await self.member_repository.create_owner(
            chat_id=chat.id,
            user_id=chat.created_by
        )

        # Автоматически добавляем участников
        if chat.chat_type in {
            ChatType.GROUP,
            ChatType.LESSON
        }:
            await self._add_group_members(
                chat=chat
            )

        return chat

    # =================================================
    # Автоматическое добавление участников группы
    # =================================================

    async def _add_group_members(
        self,
        chat: Chat
    ) -> None:
        if chat.group_id is None:
            return

        group_members = (
            await external_validation_service.get_group_members(
                group_id=chat.group_id
            )
        )

        members_to_create: list[dict] = []

        for group_member in group_members:
            user_id = group_member.get("user_id")

            if user_id is None:
                continue

            user_id = int(user_id)

            # Создатель уже добавлен как owner
            if user_id == chat.created_by:
                continue

            role_value = str(
                group_member.get(
                    "role",
                    ""
                )
            ).lower()

            # Преподаватель получает права
            # администратора чата.
            if role_value == "teacher":
                member_role = ChatMemberRole.ADMIN

            else:
                member_role = ChatMemberRole.MEMBER

            members_to_create.append(
                {
                    "user_id": user_id,
                    "member_role": member_role,
                    "added_by": chat.created_by
                }
            )

        if members_to_create:
            await self.member_repository.create_many(
                chat_id=chat.id,
                members_data=members_to_create
            )

    # =================================================
    # Добавить нового участника в существующий чат группы
    # =================================================

    async def ensure_group_chat_member(
        self,
        group_id: int,
        user_id: int,
        academic_role: str
    ) -> None:
        chat = await self.chat_repository.get_group_chat(
            group_id=group_id
        )

        if chat is None:
            return

        member_role = (
            ChatMemberRole.ADMIN
            if academic_role.lower() == "teacher"
            else ChatMemberRole.MEMBER
        )

        member = await self.member_repository.get_member(
            chat_id=chat.id,
            user_id=user_id
        )

        if member is None:
            await self.member_repository.create(
                chat_id=chat.id,
                user_id=user_id,
                member_role=member_role,
                added_by=chat.created_by
            )
            return

        if not member.is_active:
            await self.member_repository.reactivate(
                member=member,
                member_role=member_role,
                added_by=chat.created_by
            )
            return

        if member.member_role != member_role:
            await self.member_repository.set_role(
                member=member,
                member_role=member_role
            )

    # =================================================
    # Гарантировать личный чат студента с администрацией
    # =================================================

    async def ensure_admin_chat(
        self,
        student_id: int,
        admin_id: int
    ) -> Chat:
        if student_id == admin_id:
            raise ValueError(
                "Студент и администратор не могут совпадать"
            )

        # Одновременная загрузка страницы и событие RabbitMQ
        # не должны создавать два одинаковых админ-чата.
        advisory_lock_key = (
            (admin_id << 32) + student_id
        )

        await self.session.execute(
            text(
                "SELECT pg_advisory_xact_lock(:lock_key)"
            ),
            {
                "lock_key": advisory_lock_key
            }
        )

        existing_chats = (
            await self.chat_repository.get_private_chats_between(
                first_user_id=student_id,
                second_user_id=admin_id
            )
        )

        if existing_chats:
            primary_chat = existing_chats[0]

            # Дубли, созданные прежней версией, не удаляем:
            # архивирование скрывает их, но сохраняет историю.
            for duplicate_chat in existing_chats[1:]:
                await self.chat_repository.set_archived(
                    chat=duplicate_chat,
                    is_archived=True
                )

            return primary_chat

        await external_validation_service.get_available_user(
            user_id=student_id
        )

        await external_validation_service.get_available_user(
            user_id=admin_id
        )

        chat_data = ChatCreate(
            chat_type=ChatType.PRIVATE,
            title="Администрация",
            description=(
                "Если возникнут вопросы — "
                "напишите администрации."
            ),
            created_by=admin_id
        )

        chat = await self.chat_repository.create(
            chat_data=chat_data.model_dump()
        )

        await self.member_repository.create_owner(
            chat_id=chat.id,
            user_id=admin_id
        )

        await self.member_repository.create(
            chat_id=chat.id,
            user_id=student_id,
            member_role=ChatMemberRole.MEMBER,
            added_by=admin_id
        )

        await self.message_repository.create(
            message_data={
                "chat_id": chat.id,
                "sender_id": admin_id,
                "message_type": MessageType.TEXT,
                "text": (
                    "Если возникнут вопросы — "
                    "напишите администрации."
                )
            }
        )

        return chat

    # =================================================
    # Изменить чат
    # =================================================

    async def update(
        self,
        chat: Chat,
        chat_data: ChatUpdate
    ) -> Chat:
        await self._validate_management_access(
            chat=chat,
            user_id=chat_data.changed_by
        )

        update_data = chat_data.model_dump(
            exclude_unset=True,
            exclude={
                "changed_by"
            }
        )

        return await self.chat_repository.update(
            chat=chat,
            update_data=update_data
        )

    # =================================================
    # Архивировать
    # =================================================

    async def archive(
        self,
        chat: Chat,
        user_id: int
    ) -> Chat:
        await self._validate_management_access(
            chat=chat,
            user_id=user_id
        )

        if chat.is_archived:
            raise ValueError(
                "Чат уже находится в архиве"
            )

        return await self.chat_repository.set_archived(
            chat=chat,
            is_archived=True
        )

    # =================================================
    # Восстановить из архива
    # =================================================

    async def restore(
        self,
        chat: Chat,
        user_id: int
    ) -> Chat:
        await self._validate_management_access(
            chat=chat,
            user_id=user_id
        )

        if not chat.is_archived:
            raise ValueError(
                "Чат не находится в архиве"
            )

        return await self.chat_repository.set_archived(
            chat=chat,
            is_archived=False
        )

    # =================================================
    # Деактивировать
    # =================================================

    async def deactivate(
        self,
        chat: Chat,
        user_id: int
    ) -> Chat:
        await self._validate_management_access(
            chat=chat,
            user_id=user_id
        )

        if not chat.is_active:
            raise ValueError(
                "Чат уже деактивирован"
            )

        return await self.chat_repository.set_active(
            chat=chat,
            is_active=False
        )

    # =================================================
    # Активировать
    # =================================================

    async def activate(
        self,
        chat: Chat,
        user_id: int
    ) -> Chat:
        await self._validate_management_access(
            chat=chat,
            user_id=user_id
        )

        if chat.is_active:
            raise ValueError(
                "Чат уже активен"
            )

        return await self.chat_repository.set_active(
            chat=chat,
            is_active=True
        )

    # =================================================
    # Проверка права управления
    # =================================================

    async def _validate_management_access(
        self,
        chat: Chat,
        user_id: int
    ) -> None:
        member = await self.member_repository.get_member(
            chat_id=chat.id,
            user_id=user_id
        )

        if member is None or not member.is_active:
            raise ValueError(
                "Пользователь не является участником чата"
            )

        if member.member_role not in {
            ChatMemberRole.OWNER,
            ChatMemberRole.ADMIN
        }:
            raise ValueError(
                "Недостаточно прав для управления чатом"
            )
