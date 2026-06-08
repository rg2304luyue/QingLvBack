"""用户相关 Schema"""
from datetime import date, datetime
from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserProfileUpdate(BaseModel):
    nick_name: str | None = None
    gender: str | None = None
    birthday: date | None = None
    height: float | None = None
    weight: float | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    nick_name: str
    gender: str
    birthday: date | None
    height: float
    weight: float
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
