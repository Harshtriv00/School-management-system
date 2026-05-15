from pydantic import BaseModel, Field, model_validator

class ResultBase(BaseModel):
    student_roll_no: str
    student_name: str
    subject: str
    marks: int = Field(ge=0)
    total_marks: int = Field(gt=0)
    grade: str

    @model_validator(mode="after")
    def validate_marks(self):
        if self.marks > self.total_marks:
            raise ValueError("marks cannot be greater than total_marks")
        return self

class ResultCreate(ResultBase):
    pass

class ResultUpdate(BaseModel):
    subject: str | None = None
    marks: int | None = Field(default=None, ge=0)
    total_marks: int | None = Field(default=None, gt=0)
    grade: str | None = None

    @model_validator(mode="after")
    def validate_marks(self):
        if self.marks is not None and self.total_marks is not None and self.marks > self.total_marks:
            raise ValueError("marks cannot be greater than total_marks")
        return self

class ResultResponse(ResultBase):
    id: int

    class Config:
       from_attributes = True
