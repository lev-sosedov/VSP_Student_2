import json

import aio_pika
from sqlalchemy import select

from academic_service.db.db_session import AsyncSessionLocal
from academic_service.messaging.messaging_config import (
    rabbitmq_settings
)
from academic_service.models.models_branch import Branch
from academic_service.models.models_group import Group
from academic_service.models.models_group_member import GroupMember


class AcademicRpcServer:
    def __init__(self):
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None
        self.queue: aio_pika.RobustQueue | None = None

    # =====================================================
    # START
    # =====================================================

    async def start(self) -> None:
        self.connection = await aio_pika.connect_robust(
            rabbitmq_settings.url,
            heartbeat=rabbitmq_settings.heartbeat
        )

        self.channel = await self.connection.channel()

        await self.channel.set_qos(
            prefetch_count=rabbitmq_settings.prefetch_count
        )

        self.queue = await self.channel.declare_queue(
            rabbitmq_settings.academic_rpc_queue,
            durable=True
        )

        await self.queue.consume(
            self.process_message
        )

        print(
            "[Academic RPC] Server started",
            flush=True
        )

    # =====================================================
    # PROCESS MESSAGE
    # =====================================================

    async def process_message(
        self,
        message: aio_pika.IncomingMessage
    ) -> None:
        async with message.process():
            response = {
                "success": False,
                "error": "Unknown request"
            }

            try:
                request = json.loads(
                    message.body.decode()
                )

                method = request.get("method")
                payload = request.get("payload", {})

                if method == "group.get_by_id":
                    response = await self.get_group_by_id(
                        payload
                    )

                elif method == "branch.get_by_id":
                    response = await self.get_branch_by_id(
                        payload
                    )

                elif method == "group_member.exists":
                    response = await self.group_member_exists(
                        payload
                    )

                elif method == "group_members.get_by_group":
                    response = await self.get_group_members(
                        payload
                    )

                elif method == "academic.authorization.membership":
                    response = await self.authorization_membership(payload)
                elif method == "academic.authorization.user_groups":
                    response = await self.authorization_user_groups(payload)
                elif method == "academic.authorization.group_context":
                    response = await self.authorization_group_context(payload)

                else:
                    response = {
                        "success": False,
                        "error": (
                            f"Unknown RPC method: {method}"
                        )
                    }


            except Exception as error:
                response = {
                    "success": False,
                    "error": str(error)
                }

            if (
                message.reply_to
                and self.channel is not None
            ):
                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(
                            response
                        ).encode(),
                        correlation_id=(
                            message.correlation_id
                        ),
                        content_type="application/json"
                    ),
                    routing_key=message.reply_to
                )

    # =====================================================
    # GET BRANCH BY ID
    # =====================================================

    async def get_branch_by_id(
        self,
        payload: dict
    ) -> dict:
        branch_id = payload.get("branch_id")

        if branch_id is None:
            return {
                "success": False,
                "error": "branch_id is required"
            }

        async with AsyncSessionLocal() as session:
            query = select(Branch).where(
                Branch.id == int(branch_id)
            )

            result = await session.execute(query)

            branch = result.scalar_one_or_none()

            if branch is None:
                return {
                    "success": True,
                    "branch": None
                }

            return {
                "success": True,
                "branch": {
                    "id": branch.id,
                    "branch_address_id": (
                        branch.branch_address_id
                    ),
                    "is_active": branch.is_active
                }
            }

    # =====================================================
    # GET GROUP BY ID
    # =====================================================

    async def get_group_by_id(
        self,
        payload: dict
    ) -> dict:
        group_id = payload.get("group_id")

        if group_id is None:
            return {
                "success": False,
                "error": "group_id is required"
            }

        async with AsyncSessionLocal() as session:
            query = select(Group).where(
                Group.id == int(group_id)
            )

            result = await session.execute(query)

            group = result.scalar_one_or_none()

            if group is None:
                return {
                    "success": True,
                    "group": None
                }

            return {
                "success": True,
                "group": {
                    "id": group.id,
                    "branch_id": group.branch_id,
                    "is_active": getattr(
                        group,
                        "is_active",
                        True
                    )
                }
            }

    # =====================================================
    # STOP
    # =====================================================

    async def stop(self) -> None:
        if (
            self.channel is not None
            and not self.channel.is_closed
        ):
            await self.channel.close()

        if (
            self.connection is not None
            and not self.connection.is_closed
        ):
            await self.connection.close()

        self.channel = None
        self.connection = None
        self.queue = None

        print(
            "[Academic RPC] Server stopped",
            flush=True
        )

    # =====================================================
    # Проверка участия пользователя в группе
    # =====================================================

    async def group_member_exists(
        self,
        payload: dict
    ) -> dict:
        group_id = payload.get("group_id")
        user_id = payload.get("user_id")

        if group_id is None:
            return {
                "success": False,
                "error": "group_id is required"
            }

        if user_id is None:
            return {
                "success": False,
                "error": "user_id is required"
            }

        try:
            group_id = int(group_id)
            user_id = int(user_id)

        except (TypeError, ValueError):
            return {
                "success": False,
                "error": (
                    "group_id and user_id "
                    "must be integers"
                )
            }

        async with AsyncSessionLocal() as session:
            query = select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )

            result = await session.execute(query)

            group_member = result.scalar_one_or_none()

            if group_member is None:
                return {
                    "success": True,
                    "is_member": False,
                    "group_member": None
                }

            is_active = getattr(
                group_member,
                "is_active",
                True
            )

            return {
                "success": True,
                "is_member": bool(is_active),
                "group_member": {
                    "id": group_member.id,
                    "group_id": group_member.group_id,
                    "user_id": group_member.user_id,
                    "is_active": bool(is_active)
                }
            }

    # =================================================
    # Получение активных участников группы
    # =================================================

    async def get_group_members(
        self,
        payload: dict
    ) -> dict:
        group_id = payload.get("group_id")
        role = payload.get("role")

        if group_id is None:
            return {
                "success": False,
                "error": "group_id is required"
            }

        try:
            group_id = int(group_id)

        except (TypeError, ValueError):
            return {
                "success": False,
                "error": "group_id must be an integer"
            }

        async with AsyncSessionLocal() as session:
            filters = [
                GroupMember.group_id == group_id,
                GroupMember.is_active.is_(True)
            ]

            if role is not None:
                filters.append(
                    GroupMember.role == role
                )

            query = (
                select(GroupMember)
                .where(*filters)
                .order_by(GroupMember.id)
            )

            result = await session.execute(query)

            members = result.scalars().all()

            return {
                "success": True,
                "group_id": group_id,
                "members": [
                    {
                        "id": member.id,
                        "group_id": member.group_id,
                        "user_id": member.user_id,
                        "role": member.role,
                        "is_active": member.is_active
                    }
                    for member in members
                ]
            }

    async def authorization_membership(self, payload: dict) -> dict:
        try:
            user_id, group_id = int(payload["user_id"]), int(payload["group_id"])
        except (KeyError, TypeError, ValueError):
            return {"success": False, "error": "user_id and group_id are required"}
        role = payload.get("role")
        async with AsyncSessionLocal() as session:
            filters = [GroupMember.user_id == user_id, GroupMember.group_id == group_id, GroupMember.is_active.is_(True)]
            if role:
                filters.append(GroupMember.role == str(role))
            member = (await session.execute(select(GroupMember).where(*filters))).scalar_one_or_none()
            return {"success": True, "exists": member is not None, "is_active": bool(member and member.is_active), "member_role": member.role if member else None}

    async def authorization_user_groups(self, payload: dict) -> dict:
        try:
            user_id = int(payload["user_id"])
        except (KeyError, TypeError, ValueError):
            return {"success": False, "error": "user_id is required"}
        async with AsyncSessionLocal() as session:
            rows = await session.execute(select(GroupMember.group_id).join(Group, Group.id == GroupMember.group_id).where(GroupMember.user_id == user_id, GroupMember.is_active.is_(True), Group.is_active.is_(True)))
            return {"success": True, "group_ids": [int(x) for x in rows.scalars().all()]}

    async def authorization_group_context(self, payload: dict) -> dict:
        try:
            group_id = int(payload["group_id"])
        except (KeyError, TypeError, ValueError):
            return {"success": False, "error": "group_id is required"}
        async with AsyncSessionLocal() as session:
            group = await session.get(Group, group_id)
            if not group:
                return {"success": True, "context": None}
            rows = await session.execute(select(GroupMember.user_id, GroupMember.role).where(GroupMember.group_id == group_id, GroupMember.is_active.is_(True)))
            teachers = [int(uid) for uid, role in rows.all() if str(role).lower() == "teacher"]
            return {"success": True, "context": {"group_id": group.id, "teacher_ids": teachers, "branch_id": group.branch_id, "direction_id": group.direction_id, "education_plan_id": group.education_plan_id, "is_active": bool(group.is_active)}}


academic_rpc_server = AcademicRpcServer()
