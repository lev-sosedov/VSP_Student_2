from typing import Any

from academic_service.events import events_types


class AcademicEventHandlers:

    # =====================================================
    # Главный обработчик событий
    # =====================================================

    async def handle(
        self,
        event: str,
        payload: dict[str, Any]
    ):

        handlers = {
            event_types.GROUP_CREATED: self.group_created,
            event_types.GROUP_UPDATED: self.group_updated,
            event_types.GROUP_DELETED: self.group_deleted,

            event_types.MODULE_CREATED: self.module_created,
            event_types.MODULE_UPDATED: self.module_updated,
            event_types.MODULE_DELETED: self.module_deleted,

            event_types.EDUCATION_PLAN_CREATED: self.plan_created,
            event_types.EDUCATION_PLAN_UPDATED: self.plan_updated,
            event_types.EDUCATION_PLAN_DELETED: self.plan_deleted,

            event_types.DIRECTION_CREATED: self.direction_created,
            event_types.DIRECTION_UPDATED: self.direction_updated,
            event_types.DIRECTION_DELETED: self.direction_deleted,

            event_types.BRANCH_CREATED: self.branch_created,
            event_types.BRANCH_UPDATED: self.branch_updated,
            event_types.BRANCH_DELETED: self.branch_deleted,

            event_types.GROUP_MEMBER_ADDED: self.member_added,
            event_types.GROUP_MEMBER_UPDATED: self.member_updated,
            event_types.GROUP_MEMBER_REMOVED: self.member_removed,
        }

        handler = handlers.get(event)

        if handler:
            await handler(payload)
        else:
            print(f"Unknown event: {event}")

    # =====================================================
    # MODULE
    # =====================================================

    async def module_created(self, payload: dict[str, Any]):
        print("MODULE_CREATED", payload)

    async def module_updated(self, payload: dict[str, Any]):
        print("MODULE_UPDATED", payload)

    async def module_deleted(self, payload: dict[str, Any]):
        print("MODULE_DELETED", payload)

    # =====================================================
    # EDUCATION PLAN
    # =====================================================

    async def plan_created(self, payload: dict[str, Any]):
        print("PLAN_CREATED", payload)

    async def plan_updated(self, payload: dict[str, Any]):
        print("PLAN_UPDATED", payload)

    async def plan_deleted(self, payload: dict[str, Any]):
        print("PLAN_DELETED", payload)

    # =====================================================
    # DIRECTION
    # =====================================================

    async def direction_created(self, payload: dict[str, Any]):
        print("DIRECTION_CREATED", payload)

    async def direction_updated(self, payload: dict[str, Any]):
        print("DIRECTION_UPDATED", payload)

    async def direction_deleted(self, payload: dict[str, Any]):
        print("DIRECTION_DELETED", payload)

    # =====================================================
    # GROUP
    # =====================================================

    async def group_created(self, payload: dict[str, Any]):
        print("GROUP_CREATED", payload)

    async def group_updated(self, payload: dict[str, Any]):
        print("GROUP_UPDATED", payload)

    async def group_deleted(self, payload: dict[str, Any]):
        print("GROUP_DELETED", payload)

    # =====================================================
    # GROUP MEMBER
    # =====================================================

    async def member_added(self, payload: dict[str, Any]):
        print("GROUP_MEMBER_ADDED", payload)

    async def member_updated(self, payload: dict[str, Any]):
        print("GROUP_MEMBER_UPDATED", payload)

    async def member_removed(self, payload: dict[str, Any]):
        print("GROUP_MEMBER_REMOVED", payload)

    # =====================================================
    # BRANCH
    # =====================================================

    async def branch_created(self, payload: dict[str, Any]):
        print("BRANCH_CREATED", payload)

    async def branch_updated(self, payload: dict[str, Any]):
        print("BRANCH_UPDATED", payload)

    async def branch_deleted(self, payload: dict[str, Any]):
        print("BRANCH_DELETED", payload)


handlers = AcademicEventHandlers()