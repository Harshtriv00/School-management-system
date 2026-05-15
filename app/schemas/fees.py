from pydantic import BaseModel, Field
from typing import Optional
from typing import Literal

class FeeCreate(BaseModel):
    student_id: int
    student_name: str
    student_class: str
    section: str
    amount: int = Field(gt=0)
    status: Optional[Literal["pending", "paid"]] = "pending"


class FeeResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    student_class: str
    section: str
    amount: int
    status: Literal["pending", "paid"]
    
 
    class Config:
        from_attributes = True
