from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from communication_service.models.model_chat import (
    Chat
)


class ChatRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить чат по ID
    # =================================================

    async def get_by_id(
        self,
        chat_id: int,
        with_members: bool = False
    ) -> Chat | None:
        query = select(Chat).where(
            Chat.id == chat_id
        )

        if with_members:
            query = query.options(
                selectinload(
                    Chat.members
                )
            )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить список чатов
    # =================================================

    async def get_list(
        self,
        chat_type=None,
        group_id: int | None = None,
        lesson_id: int | None = None,
        created_by: int | None = None,
        is_active: bool | None = None,
        is_archived: bool | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[Chat], int]:
        filters = []

        if chat_type is not None:
            filters.append(
                Chat.chat_type == chat_type
            )

        if group_id is not None:
            filters.append(
                Chat.group_id == group_id
            )

        if lesson_id is not None:
            filters.append(
                Chat.lesson_id == lesson_id
            )

        if created_by is not None:
            filters.append(
                Chat.created_by == created_by
            )

        if is_active is not None:
            filters.append(
                Chat.is_active == is_active
            )

        if is_archived is not None:
            filters.append(
                Chat.is_archived == is_archived
            )

        chats_query = (
            select(Chat)
            .where(*filters)
            .order_by(
                Chat.updated_at.desc(),
                Chat.id.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(Chat.id))
            .where(*filters)
        )

        chats_result = await self.session.execute(
            chats_query
        )

        count_result = await self.session.execute(
            count_query
        )

        chats = list(
            chats_result.scalars().all()
        )

        total = count_result.scalar_one()

        return chats, total

    # =================================================
    # Проверка группового чата
    # =================================================

    async def get_group_chat(
        self,
        group_id: int
    ) -> Chat | None:
        query = select(Chat).where(
            Chat.group_id == group_id,
            Chat.is_active.is_(True)
        )

        result = await self.session.execute(query)

        return result.scalars().first()

    # =================================================
    # Проверка чата занятия
    # =================================================

    async def get_lesson_chat(
        self,
        lesson_id: int
    ) -> Chat | None:
        query = select(Chat).where(
            Chat.lesson_id == lesson_id,
            Chat.is_active.is_(True)
        )

        result = await self.session.execute(query)

        return result.scalars().first()

    # =================================================
    # Создать чат
    # =================================================

    async def create(
        self,
        chat_data: dict
    ) -> Chat:
        chat = Chat(
            **chat_data
        )

        self.session.add(chat)

        await self.session.flush()
        await self.session.refresh(chat)

        return chat

    # =================================================
    # Изменить чат
    # =================================================

    async def update(
        self,
        chat: Chat,
        update_data: dict
    ) -> Chat:
        for field_name, field_value in update_data.items():
            setattr(
                chat,
                field_name,
                field_value
            )

        await self.session.flush()
        await self.session.refresh(chat)

        return chat

    # =================================================
    # Установить активность
    # =================================================

    async def set_active(
        self,
        chat: Chat,
        is_active: bool
    ) -> Chat:
        chat.is_active = is_active

        await self.session.flush()
        await self.session.refresh(chat)

        return chat

    # =================================================
    # Установить архив
    # =================================================

    async def set_archived(
        self,
        chat: Chat,
        is_archived: bool
    ) -> Chat:
        chat.is_archived = is_archived

        await self.session.flush()
        await self.session.refresh(chat)

        return chat