from pydantic import BaseModel
from typing import Literal
from typing import List

class AttendanceCreate(BaseModel):
    student_id: int
    status: Literal["present", "absent"]
    date: str

class AttendanceBulkCreate(BaseModel):
    records: List[AttendanceCreate]


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    status: Literal["present", "absent"]
    date: str

    class Config:
        from_attributes = True
