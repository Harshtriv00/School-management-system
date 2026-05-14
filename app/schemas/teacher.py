from pydantic import BaseModel, EmailStr
from typing import Optional

class TeacherCreate(BaseModel):
    employee_id: str
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    subject: Optional[str] = None
    salary: Optional[int] = None


class TeacherResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    subject: Optional[str]
    salary: Optional[int]

    class Config:
        from_attributes = True 