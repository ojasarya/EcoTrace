"""Authentication request and response schemas."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(RegisterRequest):
    pass


class UserRead(BaseModel):
    id: int
    email: EmailStr


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
