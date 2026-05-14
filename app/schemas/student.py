from pydantic import BaseModel, EmailStr
from typing import Optional


class StudentBase(BaseModel):
    roll_no: str
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None


class StudentCreate(StudentBase):
    classroom_id: int


class StudentOut(BaseModel):
    id: int
    roll_no: str
    name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    address: Optional[str]
    father_name: Optional[str]
    mother_name: Optional[str]
    classroom_id: int
    class_name: Optional[str] = None
    section: Optional[str] = None

    model_config = {
        "from_attributes": True
    }