"""AI 对话路由：会话管理 + 消息收发"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    SessionCreate, SessionResponse, SessionListResponse,
    MessageResponse, MessageListResponse,
    ChatSendRequest, ChatSendResponse,
)
from app.services.ai_analysis import agent_chat

router = APIRouter(prefix="/api/chat", tags=["AI 对话"])


# ── 会话管理 ──

@router.post("/sessions", response_model=SessionResponse)
def create_session(
    body: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新会话"""
    session = ChatSession(user_id=current_user.id, title=body.title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionResponse.model_validate(session)


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户所有会话"""
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(desc(ChatSession.updated_at))
        .all()
    )
    return SessionListResponse(
        total=len(sessions),
        sessions=[SessionResponse.model_validate(s) for s in sessions],
    )


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除会话（级联删除消息）"""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.delete(session)
    db.commit()
    return {"message": "已删除"}


# ── 消息管理 ──

@router.get("/sessions/{session_id}/messages", response_model=MessageListResponse)
def list_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取会话内所有消息"""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return MessageListResponse(
        total=len(messages),
        messages=[MessageResponse.model_validate(m) for m in messages],
    )


@router.post("/sessions/{session_id}/send", response_model=ChatSendResponse)
def send_message(
    session_id: int,
    body: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """发送消息并获取 AI 回答"""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 保存用户消息
    user_msg = ChatMessage(session_id=session_id, role="user", content=body.message)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 如果是第一条消息，用它作为会话标题
    msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).count()
    if msg_count == 1:
        session.title = body.message[:50]
        db.commit()

    # 构建对话历史
    history_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in history_msgs[:-1]]

    # 调用 AI Agent（查询用户数据+收藏+历史）
    ai_reply = agent_chat(db, current_user.id, body.message, history)

    # 保存 AI 回答
    ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_reply)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ChatSendResponse(
        user_message=MessageResponse.model_validate(user_msg),
        ai_message=MessageResponse.model_validate(ai_msg),
    )
