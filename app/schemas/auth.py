from pydantic import BaseModel, EmailStr, Field

class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6)

class LoginSchema(BaseModel):
    username: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
