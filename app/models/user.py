from sqlalchemy import Column, Integer, String, Enum
from app.database import Base
from app.models.role import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

    role = Column(Enum(UserRole), default=UserRole.student) 