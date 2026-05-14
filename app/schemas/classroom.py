from pydantic import BaseModel
from typing import List
from app.schemas.student import StudentOut


class ClassroomCreate(BaseModel):
    class_name: str
    section: str


class ClassroomResponse(BaseModel):
    id: int
    class_name: str
    section: str

    total_students: int
    students: List[StudentOut]

    model_config = {
        "from_attributes": True
    }