"""AI 对话 Schema"""
from datetime import datetime
from pydantic import BaseModel


class SessionCreate(BaseModel):
    title: str = "新对话"


class SessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    total: int
    sessions: list[SessionResponse]


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    total: int
    messages: list[MessageResponse]


class ChatSendRequest(BaseModel):
    message: str


class ChatSendResponse(BaseModel):
    user_message: MessageResponse
    ai_message: MessageResponse
