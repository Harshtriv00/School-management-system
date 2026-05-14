from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("students.id"))
    status = Column(String(20))
    date = Column(String(20))