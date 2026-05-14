from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(50), nullable=False)
    section = Column(String(10), nullable=False)
    students = relationship("Student", back_populates="classroom")