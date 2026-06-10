"""用户相关 Schema"""
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserProfileUpdate(BaseModel):
    nick_name: str | None = None
    gender: Literal["男", "女"] | None = None
    birthday: date | None = None
    height: float | None = Field(None, ge=50, le=250)
    weight: float | None = Field(None, ge=10, le=300)


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
