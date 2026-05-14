from pydantic import BaseModel

class ResultBase(BaseModel):
    student_roll_no: str
    student_name: str
    subject: str
    marks: int
    total_marks: int
    grade: str

class ResultCreate(ResultBase):
    pass

class ResultUpdate(BaseModel):
    subject: str | None = None
    marks: int | None = None
    total_marks: int | None = None
    grade: str | None = None

class ResultResponse(ResultBase):
    id: int

    class Config:
       from_attributes = True