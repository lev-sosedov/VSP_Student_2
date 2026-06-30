from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from academic_service.repositories.group_member_repository import GroupMemberRepository
from academic_service.repositories.group_repository import GroupRepository
from academic_service.repositories.module_repository import ModuleRepository
from academic_service.repositories.education_plan_repository import EducationPlanRepository
from academic_service.repositories.education_plan_module_repository import EducationPlanModuleRepository
from academic_service.repositories.direction_repository import DirectionRepository
from academic_service.repositories.branch_repository import BranchRepository
from academic_service.repositories.branch_address_repository import BranchAddressRepository


from academic_service.services.group_member_service import GroupMemberService
from academic_service.services.module_service import ModuleService
from academic_service.services.education_plan_service import EducationPlanService
from academic_service.services.education_plan_module_service import EducationPlanModuleService
from academic_service.services.direction_service import DirectionService
from academic_service.services.branch_service import BranchService
from academic_service.services.branch_address import BranchAddressService


@dataclass
class Container:
    session: AsyncSession

    # repositories
    group_member_repo: GroupMemberRepository = None
    group_repo: GroupRepository = None
    module_repo: ModuleRepository = None
    plan_repo: EducationPlanRepository = None
    plan_module_repo: EducationPlanModuleRepository = None
    direction_repo: DirectionRepository = None
    branch_repo: BranchRepository = None
    branch_address_repo: BranchAddressRepository = None

    # services
    group_member_service: GroupMemberService = None
    module_service: ModuleService = None
    education_plan_service: EducationPlanService = None
    education_plan_module_service: EducationPlanModuleService = None
    direction_service: DirectionService = None
    branch_service: BranchService = None
    branch_address_service: BranchAddressService = None

    def build(self):
        # repos
        self.group_member_repo = GroupMemberRepository(self.session)
        self.group_repo = GroupRepository(self.session)
        self.module_repo = ModuleRepository(self.session)
        self.plan_repo = EducationPlanRepository(self.session)
        self.plan_module_repo = EducationPlanModuleRepository(self.session)
        self.direction_repo = DirectionRepository(self.session)
        self.branch_repo = BranchRepository(self.session)
        self.branch_address_repo = BranchAddressRepository(self.session)

        # services
        self.group_member_service = GroupMemberService(
            self.group_member_repo,
            self.group_repo
        )

        self.module_service = ModuleService(self.module_repo)

        self.education_plan_service = EducationPlanService(
            self.plan_repo,
            self.direction_repo,
            self.plan_module_repo,
            self.module_repo
        )

        self.education_plan_module_service = EducationPlanModuleService(
            self.plan_module_repo,
            self.plan_repo,
            self.module_repo
        )

        self.direction_service = DirectionService(
            self.direction_repo,
            self.plan_repo
        )

        self.branch_service = BranchService(
            self.branch_repo,
            self.branch_address_repo
        )

        self.branch_address_service = BranchAddressService(
            self.branch_address_repo
        )

        return self