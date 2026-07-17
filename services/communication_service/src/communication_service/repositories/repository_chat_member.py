from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_chat_member_role import (
    ChatMemberRole
)
from communication_service.models.model_chat_member import (
    ChatMember
)


class ChatMemberRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить участника по ID
    # =================================================

    async def get_by_id(
        self,
        member_id: int
    ) -> ChatMember | None:
        query = select(ChatMember).where(
            ChatMember.id == member_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить участника по чату и пользователю
    # =================================================

    async def get_member(
        self,
        chat_id: int,
        user_id: int
    ) -> ChatMember | None:
        query = select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == user_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

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
        filters = [
            ChatMember.chat_id == chat_id
        ]

        if is_active is not None:
            filters.append(
                ChatMember.is_active == is_active
            )

        if member_role is not None:
            filters.append(
                ChatMember.member_role == member_role
            )

        members_query = (
            select(ChatMember)
            .where(*filters)
            .order_by(
                ChatMember.is_active.desc(),
                ChatMember.joined_at,
                ChatMember.id
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(ChatMember.id))
            .where(*filters)
        )

        members_result = await self.session.execute(
            members_query
        )

        count_result = await self.session.execute(
            count_query
        )

        members = list(
            members_result.scalars().all()
        )

        total = count_result.scalar_one()

        return members, total

    # =================================================
    # Создать владельца
    # =================================================

    async def create_owner(
        self,
        chat_id: int,
        user_id: int
    ) -> ChatMember:
        member = ChatMember(
            chat_id=chat_id,
            user_id=user_id,
            member_role=ChatMemberRole.OWNER,
            added_by=user_id,
            is_active=True
        )

        self.session.add(member)

        await self.session.flush()
        await self.session.refresh(member)

        return member

    # =================================================
    # Создать участника
    # =================================================

    async def create(
        self,
        chat_id: int,
        user_id: int,
        member_role: ChatMemberRole,
        added_by: int
    ) -> ChatMember:
        member = ChatMember(
            chat_id=chat_id,
            user_id=user_id,
            member_role=member_role,
            added_by=added_by,
            is_active=True,
            joined_at=datetime.utcnow(),
            left_at=None
        )

        self.session.add(member)

        await self.session.flush()
        await self.session.refresh(member)

        return member

    # =================================================
    # Повторно активировать участника
    # =================================================

    async def reactivate(
        self,
        member: ChatMember,
        member_role: ChatMemberRole,
        added_by: int
    ) -> ChatMember:
        member.member_role = member_role
        member.added_by = added_by
        member.is_active = True
        member.joined_at = datetime.utcnow()
        member.left_at = None

        await self.session.flush()
        await self.session.refresh(member)

        return member

    # =================================================
    # Изменить роль
    # =================================================

    async def set_role(
        self,
        member: ChatMember,
        member_role: ChatMemberRole
    ) -> ChatMember:
        member.member_role = member_role

        await self.session.flush()
        await self.session.refresh(member)

        return member

    # =================================================
    # Деактивировать
    # =================================================

    async def deactivate(
        self,
        member: ChatMember
    ) -> ChatMember:
        member.is_active = False
        member.left_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(member)

        return member

    # =================================================
    # Активировать
    # =================================================

    async def activate(
        self,
        member: ChatMember
    ) -> ChatMember:
        member.is_active = True
        member.left_at = None
        member.joined_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(member)

        return member

    # =================================================
    # Создать несколько участников
    # =================================================

    async def create_many(
        self,
        chat_id: int,
        members_data: list[dict]
    ) -> list[ChatMember]:
        members: list[ChatMember] = []

        for member_data in members_data:
            member = ChatMember(
                chat_id=chat_id,
                user_id=member_data["user_id"],
                member_role=member_data["member_role"],
                added_by=member_data.get("added_by"),
                is_active=True,
                joined_at=datetime.utcnow(),
                left_at=None
            )

            self.session.add(member)
            members.append(member)

        await self.session.flush()

        for member in members:
            await self.session.refresh(member)

        return members

    # =================================================
    # Получить пользователей для уведомления
    # =================================================

    async def get_notification_user_ids(
        self,
        chat_id: int,
        exclude_user_id: int | None = None
    ) -> list[int]:
        filters = [
            ChatMember.chat_id == chat_id,
            ChatMember.is_active.is_(True),
            ChatMember.is_muted.is_(False)
        ]

        if exclude_user_id is not None:
            filters.append(
                ChatMember.user_id != exclude_user_id
            )

        query = (
            select(ChatMember.user_id)
            .where(*filters)
            .order_by(ChatMember.user_id)
        )

        result = await self.session.execute(query)

        return list(
            result.scalars().all()
        )