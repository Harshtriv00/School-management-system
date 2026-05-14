from sqlalchemy import Column, Integer, String
from app.database import Base

class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    student_name = Column(String(100), nullable=False)
    student_class = Column(String(50), nullable=False)
    section = Column(String(10), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String(20), default="pending") 