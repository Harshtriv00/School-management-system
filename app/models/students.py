from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    roll_no = Column(String(30), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True)
    phone = Column(String(20))
    address = Column(String(255))
    father_name = Column(String(100))
    mother_name = Column(String(100))
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    classroom = relationship("Classroom", back_populates="students")