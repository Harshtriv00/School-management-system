from pydantic import BaseModel
from typing import Optional

class FeeCreate(BaseModel):
    student_id: int
    student_name: str
    student_class: str
    section: str
    amount: int
    status: Optional[str] = "pending"


class FeeResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    student_class: str
    section: str
    amount: int
    status: str
    
 
    class Config:
        from_attributes = True