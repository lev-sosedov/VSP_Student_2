from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from academic_service.db.session import get_session

# repositories
from academic_service.repositories.repository_group_member import GroupMemberRepository
from academic_service.repositories.repository_group import GroupRepository

from academic_service.repositories.repository_module import ModuleRepository
from academic_service.repositories.repository_education_plan import EducationPlanRepository
from academic_service.repositories.repository_education_plan_module import EducationPlanModuleRepository

from academic_service.repositories.repository_direction import DirectionRepository

from academic_service.repositories.repository_branch import BranchRepository
from academic_service.repositories.repository_branch_address import BranchAddressRepository

from academic_service.repositories.repository_group import GroupRepository

# services
from academic_service.services.service_group_member import GroupMemberService
from academic_service.services.service_module import ModuleService
from academic_service.services.service_education_plan import EducationPlanService
from academic_service.services.service_education_plan_module import EducationPlanModuleService
from academic_service.services.service_direction import DirectionService
from academic_service.services.service_branch import BranchService
from academic_service.services.service_branch_address import BranchAddressService


from academic_service.services.service_group import GroupService
# =========================
# Repositories
# =========================

def get_group_member_repo(session: AsyncSession = Depends(get_session)):
    return GroupMemberRepository(session)


def get_group_repo(session: AsyncSession = Depends(get_session)):
    return GroupRepository(session)


def get_module_repo(session: AsyncSession = Depends(get_session)):
    return ModuleRepository(session)


def get_plan_repo(session: AsyncSession = Depends(get_session)):
    return EducationPlanRepository(session)


def get_plan_module_repo(session: AsyncSession = Depends(get_session)):
    return EducationPlanModuleRepository(session)


def get_direction_repo(session: AsyncSession = Depends(get_session)):
    return DirectionRepository(session)


def get_branch_repo(session: AsyncSession = Depends(get_session)):
    return BranchRepository(session)


def get_branch_address_repo(session: AsyncSession = Depends(get_session)):
    return BranchAddressRepository(session)


# =========================
# Services
# =========================

def get_group_member_service(
    session: AsyncSession = Depends(get_session)
):
    return GroupMemberService(
        repo=GroupMemberRepository(session),
        group_repo=GroupRepository(session)
    )


def get_module_service(
    session: AsyncSession = Depends(get_session)
):
    return ModuleService(
        repo=ModuleRepository(session)
    )


def get_education_plan_service(
    session: AsyncSession = Depends(get_session)
):
    return EducationPlanService(
        plan_repo=EducationPlanRepository(session),
        direction_repo=DirectionRepository(session),
        plan_module_repo=EducationPlanModuleRepository(session),
        module_repo=ModuleRepository(session)
    )


def get_education_plan_module_service(
    session: AsyncSession = Depends(get_session)
):
    return EducationPlanModuleService(
        repo=EducationPlanModuleRepository(session),
        plan_repo=EducationPlanRepository(session),
        module_repo=ModuleRepository(session)
    )


def get_direction_service(
    session: AsyncSession = Depends(get_session)
):
    return DirectionService(
        repo=DirectionRepository(session),
        plan_repo=EducationPlanRepository(session)
    )


def get_branch_service(
    session: AsyncSession = Depends(get_session)
):
    return BranchService(
        branch_repo=BranchRepository(session),
        address_repo=BranchAddressRepository(session)
    )


def get_branch_address_service(
    session: AsyncSession = Depends(get_session)
):
    return BranchAddressService(
        BranchAddressRepository(session)
    )

# def get_group_service(session: AsyncSession = Depends(get_session)):
#     return GroupService(
#         repo=GroupRepository(session)
#     )

def get_group_service(
        session: AsyncSession = Depends(get_session)
):

    return GroupService(
        GroupRepository(session),
        BranchRepository(session),
        DirectionRepository(session),
        EducationPlanRepository(session)
    )