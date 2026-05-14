from sqlalchemy import Column, Integer, String
from app.database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)

    subject_name = Column(String(100), nullable=False)
    subject_code = Column(String(30), unique=True)
    teacher_name = Column(String(100))
    class_name = Column(String(50))