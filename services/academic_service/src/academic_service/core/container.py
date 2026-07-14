from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from academic_service.repositories.repository_group_member import GroupMemberRepository
from academic_service.repositories.repository_group import GroupRepository
from academic_service.repositories.repository_module import ModuleRepository
from academic_service.repositories.repository_education_plan import EducationPlanRepository
from academic_service.repositories.repository_education_plan_module import EducationPlanModuleRepository
from academic_service.repositories.repository_direction import DirectionRepository
from academic_service.repositories.repository_branch import BranchRepository
from academic_service.repositories.repository_branch_address import BranchAddressRepository


from academic_service.services.service_group_member import GroupMemberService
from academic_service.services.service_module import ModuleService
from academic_service.services.service_education_plan import EducationPlanService
from academic_service.services.service_education_plan_module import EducationPlanModuleService
from academic_service.services.service_direction import DirectionService
from academic_service.services.service_branch import BranchService
from academic_service.services.service_branch_address import BranchAddressService


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