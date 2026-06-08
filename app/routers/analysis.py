"""AI 分析路由：健康报告 + 对话 + Agent"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.analysis import ChatRequest, ChatResponse, AnalysisReport, AgentRequest, AgentResponse
from app.services.ai_analysis import analyze_health, chat_with_advisor, agent_chat

router = APIRouter(prefix="/api/analysis", tags=["AI 分析"])


@router.get("/report", response_model=AnalysisReport)
def get_report(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AnalysisReport(**analyze_health(db, current_user.id))


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reply = chat_with_advisor(db, current_user.id, body.message)
    return ChatResponse(content=reply)


@router.post("/agent", response_model=AgentResponse)
def agent(body: AgentRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """健康 Agent：查询用户数据+收藏，结合对话历史，AI 回答"""
    reply = agent_chat(db, current_user.id, body.message, body.history)
    return AgentResponse(content=reply)
