"""AI 分析 Schema"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(max_length=2000)


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
    message: str = Field(max_length=2000)
    history: list[dict] = Field(default_factory=list, max_length=50)  # 对话历史，最多 50 条


class AgentResponse(BaseModel):
    role: str = "assistant"
    content: str
