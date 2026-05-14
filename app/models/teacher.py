from sqlalchemy import Column, Integer, String
from app.database import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String(30), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=True)  # allow null
    phone = Column(String(20))
    subject = Column(String(100))
    salary = Column(Integer) 