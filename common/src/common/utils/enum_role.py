from enum import Enum


# основные роли
class RoleType(str, Enum):
    USER = "user" # зарегистрированный пользователь
    PARENT = "parent" # родитель
    STUDENT = "student" # студент
    TEACHER = "teacher" # учитель
    ADMIN = "admin" # администратор
