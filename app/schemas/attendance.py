from pydantic import BaseModel
from datetime import date
from typing import Literal
from typing import List

class AttendanceCreate(BaseModel):
    student_id: int
    status: Literal["present", "absent"]
    date: date

class AttendanceBulkCreate(BaseModel):
    records: List[AttendanceCreate]


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    status: Literal["present", "absent"]
    date: date

    class Config:
        from_attributes = True
