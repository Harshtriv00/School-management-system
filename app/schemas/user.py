from pydantic import BaseModel, EmailStr
from app.models.role import UserRole

# BASE

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

 
    class Config:
        from_attributes = True 
