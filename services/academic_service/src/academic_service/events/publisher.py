from typing import Any

from academic_service.messaging.publisher import publisher
from academic_service.events import event_types


class AcademicEventPublisher:

    # =====================================================
    # Внутренняя отправка события
    # =====================================================

    async def _publish(
        self,
        event_type: str,
        payload: dict[str, Any]
    ):

        await publisher.publish(
            routing_key=event_type,
            message={
                "event": event_type,
                "payload": payload
            }
        )

    # =====================================================
    # MODULE
    # =====================================================

    async def publish_module_created(self, payload: dict[str, Any]):
        await self._publish(event_types.MODULE_CREATED, payload)

    async def publish_module_updated(self, payload: dict[str, Any]):
        await self._publish(event_types.MODULE_UPDATED, payload)

    async def publish_module_deleted(self, payload: dict[str, Any]):
        await self._publish(event_types.MODULE_DELETED, payload)

    async def publish_module_activated(self, payload: dict[str, Any]):
        await self._publish(event_types.MODULE_ACTIVATED, payload)

    async def publish_module_deactivated(self, payload: dict[str, Any]):
        await self._publish(event_types.MODULE_DEACTIVATED, payload)

    # =====================================================
    # EDUCATION PLAN
    # =====================================================

    async def publish_plan_created(self, payload: dict[str, Any]):
        await self._publish(event_types.EDUCATION_PLAN_CREATED, payload)

    async def publish_plan_updated(self, payload: dict[str, Any]):
        await self._publish(event_types.EDUCATION_PLAN_UPDATED, payload)

    async def publish_plan_deleted(self, payload: dict[str, Any]):
        await self._publish(event_types.EDUCATION_PLAN_DELETED, payload)

    async def publish_plan_activated(self, payload: dict[str, Any]):
        await self._publish(event_types.EDUCATION_PLAN_ACTIVATED, payload)

    async def publish_plan_deactivated(self, payload: dict[str, Any]):
        await self._publish(event_types.EDUCATION_PLAN_DEACTIVATED, payload)

    # =====================================================
    # EDUCATION PLAN MODULE
    # =====================================================

    async def publish_plan_module_created(self, payload: dict[str, Any]):
        await self._publish(event_types.PLAN_MODULE_CREATED, payload)

    async def publish_plan_module_updated(self, payload: dict[str, Any]):
        await self._publish(event_types.PLAN_MODULE_UPDATED, payload)

    async def publish_plan_module_deleted(self, payload: dict[str, Any]):
        await self._publish(event_types.PLAN_MODULE_DELETED, payload)

    async def publish_plan_module_reordered(self, payload: dict[str, Any]):
        await self._publish(event_types.PLAN_MODULE_REORDERED, payload)

    # =====================================================
    # DIRECTION
    # =====================================================

    async def publish_direction_created(self, payload: dict[str, Any]):
        await self._publish(event_types.DIRECTION_CREATED, payload)

    async def publish_direction_updated(self, payload: dict[str, Any]):
        await self._publish(event_types.DIRECTION_UPDATED, payload)

    async def publish_direction_deleted(self, payload: dict[str, Any]):
        await self._publish(event_types.DIRECTION_DELETED, payload)

    async def publish_direction_activated(self, payload: dict[str, Any]):
        await self._publish(event_types.DIRECTION_ACTIVATED, payload)

    async def publish_direction_deactivated(self, payload: dict[str, Any]):
        await self._publish(event_types.DIRECTION_DEACTIVATED, payload)

    # =====================================================
    # GROUP
    # =====================================================

    async def publish_group_created(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_CREATED, payload)

    async def publish_group_updated(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_UPDATED, payload)

    async def publish_group_deleted(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_DELETED, payload)

    async def publish_group_activated(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_ACTIVATED, payload)

    async def publish_group_deactivated(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_DEACTIVATED, payload)

    # =====================================================
    # GROUP MEMBER
    # =====================================================

    async def publish_member_added(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_MEMBER_ADDED, payload)

    async def publish_member_updated(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_MEMBER_UPDATED, payload)

    async def publish_member_removed(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_MEMBER_REMOVED, payload)

    async def publish_member_activated(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_MEMBER_ACTIVATED, payload)

    async def publish_member_deactivated(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_MEMBER_DEACTIVATED, payload)

    async def publish_member_transferred(self, payload: dict[str, Any]):
        await self._publish(event_types.GROUP_MEMBER_TRANSFERRED, payload)

    # =====================================================
    # BRANCH
    # =====================================================

    async def publish_branch_created(self, payload: dict[str, Any]):
        await self._publish(event_types.BRANCH_CREATED, payload)

    async def publish_branch_updated(self, payload: dict[str, Any]):
        await self._publish(event_types.BRANCH_UPDATED, payload)

    async def publish_branch_deleted(self, payload: dict[str, Any]):
        await self._publish(event_types.BRANCH_DELETED, payload)

    async def publish_branch_activated(self, payload: dict[str, Any]):
        await self._publish(event_types.BRANCH_ACTIVATED, payload)

    async def publish_branch_deactivated(self, payload: dict[str, Any]):
        await self._publish(event_types.BRANCH_DEACTIVATED, payload)

    # =====================================================
    # BRANCH ADDRESS
    # =====================================================

    async def publish_branch_address_created(self, payload: dict[str, Any]):
        await self._publish(event_types.BRANCH_ADDRESS_CREATED, payload)

    async def publish_branch_address_updated(self, payload: dict[str, Any]):
        await self._publish(event_types.BRANCH_ADDRESS_UPDATED, payload)

    async def publish_branch_address_deleted(self, payload: dict[str, Any]):
        await self._publish(event_types.BRANCH_ADDRESS_DELETED, payload)


event_publisher = AcademicEventPublisher()