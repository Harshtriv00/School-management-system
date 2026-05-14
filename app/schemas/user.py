from pydantic import BaseModel, EmailStr

# BASE

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str   # admin / teacher / student

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

 
    class Config:
        from_attributes = True 