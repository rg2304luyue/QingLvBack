"""AI 分析 Schema"""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str


class AnalysisReport(BaseModel):
    overall_score: int
    score_level: str
    summary: str
    highlights: list[str]
    concerns: list[str]
    suggestions: list[str]
    weight_trend: str
    bp_assessment: str
    hr_assessment: str
    bs_assessment: str


class AgentRequest(BaseModel):
    message: str
    history: list[dict] = []  # 对话历史 [{role: "user"/"assistant", content: "..."}]


class AgentResponse(BaseModel):
    role: str = "assistant"
    content: str
