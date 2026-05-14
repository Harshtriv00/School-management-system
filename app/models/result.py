from sqlalchemy import Column, Integer, String
from app.database import Base

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)

    student_roll_no = Column(String(30), nullable=False)
    student_name = Column(String(100))
    subject = Column(String(100))
    marks = Column(Integer)
    total_marks = Column(Integer, default=100)
    grade = Column(String(10)) 