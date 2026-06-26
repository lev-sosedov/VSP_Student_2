from sqlalchemy.orm import DeclarativeBase

from academic_service.models.branch import Branch
from academic_service.models.branch_address import BranchAddress
from academic_service.models.direction import Direction
from academic_service.models.education_plans import EducationPlan
from academic_service.models.education_plan_modules import EducationPlanModule
from academic_service.models.module import Module
from academic_service.models.group import Group
from academic_service.models.group_member import GroupMember


class Base(DeclarativeBase):
    pass