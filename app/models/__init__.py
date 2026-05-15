from app.models.attendance import Attendance
from app.models.classroom import Classroom
from app.models.fees import Fee
from app.models.result import Result
from app.models.role import UserRole
from app.models.students import Student
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.user import User

__all__ = [
    "Attendance",
    "Classroom",
    "Fee",
    "Result",
    "register_models",
    "Student",
    "Subject",
    "Teacher",
    "User",
    "UserRole",
]


def register_models():
    """Import this package before create_all so SQLAlchemy sees every model."""
    return None
