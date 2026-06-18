"""
AI 健康分析服务
- LLM 可用 → LangGraph ReAct Agent（支持工具调用）
- LLM 不可用 → 规则引擎回退
"""
import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models.health import HealthRecord

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  规则引擎（LLM 不可用时的回退方案）
# ═══════════════════════════════════════════════════════════════

def _get_recent_records(db: Session, user_id: int, days: int = 30):
    start = datetime.now() - timedelta(days=days)
    records = (
        db.query(HealthRecord)
        .filter(HealthRecord.user_id == user_id, HealthRecord.timestamp >= start)
        .order_by(HealthRecord.timestamp.desc())
        .all()
    )
    return records, len(records)


def _rule_based_analysis(db: Session, user_id: int) -> dict:
    records, _ = _get_recent_records(db, user_id, days=30)

    if not records:
        return {
            "overall_score": 0, "score_level": "无数据",
            "summary": "暂无足够的健康数据进行分析。请录入健康数据后再试。",
            "highlights": [], "concerns": [], "suggestions": ["开始录入你的第一次健康数据吧！"],
            "weight_trend": "无数据", "bp_assessment": "无数据",
            "hr_assessment": "无数据", "bs_assessment": "无数据",
        }

    latest = records[0]
    scores = {"bmi": 25, "bp": 20, "hr": 15, "bs": 15, "exercise": 25}
    concerns: list[str] = []
    highlights: list[str] = []
    suggestions: list[str] = []

    # BMI
    bmi = latest.bmi
    if 18.5 <= bmi < 24:
        scores["bmi"] = 25
        highlights.append(f"BMI {bmi:.1f} 处于正常范围")
    elif 24 <= bmi < 28:
        scores["bmi"] = 18
        concerns.append(f"BMI {bmi:.1f} 偏胖")
        suggestions.append("建议控制饮食热量，每天保持 30 分钟有氧运动")
    elif bmi >= 28:
        scores["bmi"] = 10
        concerns.append(f"BMI {bmi:.1f} 属于肥胖范围")
        suggestions.append("建议制定系统性减重计划，每周减 0.5-1 公斤为宜")
    elif bmi > 0:
        scores["bmi"] = 15
        concerns.append(f"BMI {bmi:.1f} 偏瘦")
        suggestions.append("建议增加优质蛋白和碳水化合物摄入")

    # 血压
    sys_val = latest.blood_pressure_systolic
    dia_val = latest.blood_pressure_diastolic
    if sys_val > 0:
        if sys_val < 130 and dia_val < 85:
            scores["bp"] = 20
            highlights.append(f"血压 {sys_val}/{dia_val} mmHg 正常")
        elif sys_val < 140 and dia_val < 90:
            scores["bp"] = 16
            concerns.append(f"血压 {sys_val}/{dia_val} mmHg 处于正常高值")
            suggestions.append("建议低盐饮食，每周监测血压变化")
        else:
            scores["bp"] = 10
            concerns.append(f"血压 {sys_val}/{dia_val} mmHg 偏高")
            suggestions.append("血压持续偏高，建议就医咨询并保持低盐低脂饮食")
    else:
        scores["bp"] = 12

    # 心率
    hr = latest.heart_rate
    if 60 <= hr <= 80:
        scores["hr"] = 15
        highlights.append(f"静息心率 {hr} 次/分 理想")
    elif 50 <= hr <= 100:
        scores["hr"] = 12
    elif hr > 0:
        scores["hr"] = 8
        concerns.append(f"心率 {hr} 次/分 异常")
        suggestions.append("建议关注心率变化，避免咖啡因和过度疲劳")

    # 血糖
    bs = latest.blood_sugar
    if 3.9 <= bs <= 6.1:
        scores["bs"] = 15
        highlights.append(f"血糖 {bs:.1f} mmol/L 正常")
    elif 3.9 <= bs <= 7.8:
        scores["bs"] = 12
    elif bs > 0:
        scores["bs"] = 8
        concerns.append(f"血糖 {bs:.1f} mmol/L 偏高")
        suggestions.append("建议控制碳水化合物摄入，餐后适度运动")

    # 运动 / 睡眠
    steps = latest.step_count
    sleep_val = latest.sleep_hours
    ex_score = 5
    if steps >= 8000:
        ex_score += 15
        highlights.append(f"日均步数 {steps} 达标")
    elif steps >= 5000:
        ex_score += 10
    if 7 <= sleep_val <= 9:
        ex_score += 10
        highlights.append(f"睡眠 {sleep_val:.1f}h 良好")
    elif sleep_val >= 6:
        ex_score += 7
    elif sleep_val > 0:
        suggestions.append(f"睡眠不足（{sleep_val:.1f}h），建议提前入睡，保证 7-8 小时")
    scores["exercise"] = min(ex_score, 25)

    overall = sum(scores.values())
    if overall >= 90: level = "优秀"
    elif overall >= 80: level = "良好"
    elif overall >= 70: level = "一般"
    elif overall >= 60: level = "偏差"
    else: level = "需关注"

    w_values = [r.weight for r in records if r.weight > 0]
    w_dates = [r.timestamp.strftime("%m/%d") for r in records if r.weight > 0]
    weight_trend = "无数据"
    if len(w_values) >= 2:
        diff = w_values[0] - w_values[-1]
        if diff < -0.5:
            weight_trend = f"体重下降 {abs(diff):.1f} 公斤（{w_dates[-1]} → {w_dates[0]}），趋势良好"
        elif diff > 0.5:
            weight_trend = f"体重上升 {diff:.1f} 公斤（{w_dates[-1]} → {w_dates[0]}），建议关注"
        else:
            weight_trend = f"体重稳定（{w_dates[-1]} → {w_dates[0]}），波动 < 0.5 公斤"

    return {
        "overall_score": overall, "score_level": level,
        "summary": (
            f"综合健康评分 {overall}/100，等级「{level}」。"
            f"BMI({scores['bmi']}/25)、血压({scores['bp']}/20)、"
            f"心率({scores['hr']}/15)、血糖({scores['bs']}/15)、"
            f"运动睡眠({scores['exercise']}/25)。"
        ),
        "highlights": highlights[:3] or ["各项指标正常，继续保持"],
        "concerns": concerns[:3],
        "suggestions": suggestions[:4] or ["继续保持良好的生活习惯"],
        "weight_trend": weight_trend,
        "bp_assessment": f"血压 {sys_val}/{dia_val} mmHg" if sys_val > 0 else "暂无血压数据",
        "hr_assessment": f"心率 {hr} 次/分" if hr > 0 else "暂无心率数据",
        "bs_assessment": f"血糖 {bs:.1f} mmol/L" if bs > 0 else "暂无血糖数据",
    }


def _llm_analysis(db: Session, user_id: int) -> dict:
    """LLM 生成健康评估报告（非 Agent 模式，直接调用 LLM）"""
    import re
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage

    records, _ = _get_recent_records(db, user_id, days=30)
    if not records:
        return _rule_based_analysis(db, user_id)

    data_lines = ["最近30天健康数据："]
    for r in records[:30]:
        parts = [f"  {r.timestamp.strftime('%m/%d')}:"]
        if r.weight > 0: parts.append(f"体重{r.weight}公斤")
        if r.bmi > 0: parts.append(f"BMI{r.bmi:.1f}")
        if r.blood_pressure_systolic > 0: parts.append(f"血压{r.blood_pressure_systolic}/{r.blood_pressure_diastolic}")
        if r.heart_rate > 0: parts.append(f"心率{r.heart_rate}")
        if r.blood_sugar > 0: parts.append(f"血糖{r.blood_sugar}")
        if r.step_count > 0: parts.append(f"步数{r.step_count}")
        if r.sleep_hours > 0: parts.append(f"睡眠{r.sleep_hours:.1f}h")
        if len(parts) > 1:
            data_lines.append("，".join(parts))

    data_text = "\n".join(data_lines)

    system_prompt = """你是一名专业的健康数据分析师。根据用户的健康数据，生成评估报告。
严格按以下 JSON 格式返回（只返回 JSON，不要其他文字）：

{
  "overall_score": 数字0-100,
  "score_level": "优秀/良好/一般/偏差/需关注",
  "summary": "一段 100 字以内的综合概述",
  "highlights": ["做得好的方面"],
  "concerns": ["需要关注的问题"],
  "suggestions": ["具体的改进建议"],
  "weight_trend": "体重趋势一句话",
  "bp_assessment": "血压评估一句话",
  "hr_assessment": "心率评估一句话",
  "bs_assessment": "血糖评估一句话"
}

评分参考：BMI正常18.5-24，血压<130/85正常，静息心率60-80理想，空腹血糖3.9-6.1正常。
指标为 0 表示没有数据。建议要具体可执行。"""

    try:
        llm = ChatOpenAI(
            model=settings.llm_model,
            openai_api_key=settings.llm_api_key,
            openai_api_base=settings.llm_base_url,
            temperature=0.3, max_tokens=800,
        )
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=data_text)])
        text = response.content.strip()
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            text = match.group()
        return json.loads(text)
    except Exception as e:
        logger.warning(f"LLM 分析失败，回退规则引擎: {e}")
        return _rule_based_analysis(db, user_id)


# ═══════════════════════════════════════════════════════════════
#  LangGraph ReAct Agent（支持工具调用的智能对话）
# ═══════════════════════════════════════════════════════════════

def _run_agent_loop(db: Session, user_id: int, messages: list) -> str:
    """
    手动实现 ReAct Agent 循环
    使用 LangChain 原生 tool calling，不依赖 langgraph.prebuilt
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, AIMessage, ToolMessage

    from app.services.agent_tools import create_tools

    tools = create_tools(db, user_id)

    # 创建 LLM 并绑定工具
    llm = ChatOpenAI(
        model=settings.llm_model,
        openai_api_key=settings.llm_api_key,
        openai_api_base=settings.llm_base_url,
        temperature=0.7,
        max_tokens=1500,
    )
    llm_with_tools = llm.bind_tools(tools)

    system_prompt = """你是"清律健康顾问"，一个专业、温暖的 AI 健康助手。

## 你的能力
你可以通过工具查询用户的健康数据，包括：
- 个人信息（身高、体重、BMI）
- 健康记录（体重、血压、心率、血糖、步数、睡眠）
- 饮水数据、打卡记录、体重目标
- 收藏的健康知识文章
- 营养分析、运动计划生成、趋势预测、健康风险评估

## 单位说明
- 体重单位为「公斤」
- 血压单位为 mmHg（收缩压/舒张压）
- 血糖单位为 mmol/L
- 心率单位为 次/分

## 回答原则
1. 当用户询问健康数据时，先用工具查询真实数据，再基于数据回答
2. 当用户询问饮食/运动建议时，用工具获取身体数据后给出个性化建议
3. 如果用户有体重目标，计算当前与目标的差距并给出进度评估
4. 回答要专业、有同理心、简明扼要
5. 涉及严重健康风险时，提醒用户及时就医
6. 不要编造用户的健康数据，只使用工具返回的数据
7. 如果没有相关数据，坦诚告知并给出一般性建议
8. 使用 Markdown 格式（**加粗**、列表等）让回答更清晰"""

    # 构建完整消息列表
    all_messages = [SystemMessage(content=system_prompt)] + messages

    # 构建工具名 → 函数的映射
    tool_map = {t.name: t for t in tools}

    # ReAct 循环（最多 5 轮工具调用）
    for _ in range(6):
        response = llm_with_tools.invoke(all_messages)

        # 如果没有工具调用，直接返回回答
        if not response.tool_calls:
            return response.content.strip()

        # 有工具调用：执行工具并把结果加入消息
        all_messages.append(response)
        for tc in response.tool_calls:
            tool_name = tc["name"]
            tool_args = tc["args"]
            tool_id = tc["id"]

            logger.info(f"[Agent] 调用工具: {tool_name}({tool_args})")

            # 执行工具
            try:
                tool_func = tool_map.get(tool_name)
                if tool_func:
                    # 工具接收单个字符串参数或无参数
                    if tool_args:
                        result = tool_func.invoke(tool_args)
                    else:
                        result = tool_func.invoke({})
                else:
                    result = f"未知工具: {tool_name}"
            except Exception as e:
                result = f"工具执行出错: {str(e)}"
                logger.warning(f"[Agent] 工具 {tool_name} 执行失败: {e}")

            logger.info(f"[Agent] 工具结果: {str(result)[:200]}")
            all_messages.append(ToolMessage(content=str(result), tool_call_id=tool_id))

    # 超过最大轮次，返回最后的回答
    return response.content.strip() if response else "抱歉，处理超时，请简化您的问题。"


# ═══════════════════════════════════════════════════════════════
#  公共接口
# ═══════════════════════════════════════════════════════════════

def analyze_health(db: Session, user_id: int) -> dict:
    """健康评估报告（规则引擎 / LLM）"""
    if settings.llm_api_key:
        return _llm_analysis(db, user_id)
    return _rule_based_analysis(db, user_id)


def chat_with_advisor(db: Session, user_id: int, message: str) -> str:
    """简单健康顾问对话（无工具调用，适合轻量场景）"""
    from app.models.user import User

    user = db.query(User).filter(User.id == user_id).first()
    profile_parts = []
    if user:
        if user.gender: profile_parts.append(f"性别：{user.gender}")
        if user.height > 0: profile_parts.append(f"身高：{user.height}cm")
        if user.weight > 0: profile_parts.append(f"体重：{user.weight}公斤")
        if user.birthday:
            age = int((datetime.now().date() - user.birthday).days / 365.25)
            profile_parts.append(f"年龄：约{age}岁")
    profile_context = "，".join(profile_parts) if profile_parts else "暂无个人信息"

    records, _ = _get_recent_records(db, user_id, days=60)
    data_lines = []
    for r in records[:30]:
        parts = [f"{r.timestamp.strftime('%m/%d')}: "]
        if r.weight > 0: parts.append(f"体重{r.weight}公斤")
        if r.blood_pressure_systolic > 0: parts.append(f"血压{r.blood_pressure_systolic}/{r.blood_pressure_diastolic}")
        if r.heart_rate > 0: parts.append(f"心率{r.heart_rate}")
        if r.blood_sugar > 0: parts.append(f"血糖{r.blood_sugar}")
        if r.step_count > 0: parts.append(f"步数{r.step_count}")
        if len(parts) > 1:
            data_lines.append("，".join(parts))

    health_context = "\n".join(data_lines[:20]) if data_lines else "暂无近期健康数据"
    system_prompt = (
        f'你是专业健康顾问"清律健康顾问"。\n'
        f'用户个人信息：{profile_context}\n'
        f'用户健康数据：\n{health_context}\n\n'
        "请基于数据回答用户问题。数据不足时如实告知。回答专业、有同理心、简明扼要。"
    )

    if not settings.llm_api_key:
        analysis = _rule_based_analysis(db, user_id)
        return (
            "当前未配置 AI 模型（LLM_API_KEY 为空）。\n\n"
            f"规则引擎分析：{analysis['summary']}\n\n"
            "如需 AI 对话功能，请在 .env 中配置 LLM_API_KEY。"
        )

    try:
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage, SystemMessage
        llm = ChatOpenAI(
            model=settings.llm_model,
            openai_api_key=settings.llm_api_key,
            openai_api_base=settings.llm_base_url,
            temperature=0.7, max_tokens=600,
        )
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=message)])
        return response.content.strip()
    except Exception as e:
        logger.warning(f"chat_with_advisor LLM 调用失败: {e}")
        return "AI 服务暂时不可用，请稍后再试。"


def agent_chat(db: Session, user_id: int, message: str, history: list[dict]) -> str:
    """
    健康 Agent 对话（LangGraph ReAct Agent + Tools）
    支持工具调用：查询数据、营养分析、运动计划、趋势预测等
    """
    if not settings.llm_api_key:
        # 无 LLM 时回退到简单模式
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        records, _ = _get_recent_records(db, user_id, days=7)
        health_lines = []
        for r in records:
            parts = [f"{r.timestamp.strftime('%m/%d')}: "]
            if r.weight > 0: parts.append(f"体重{r.weight}公斤")
            if r.blood_pressure_systolic > 0: parts.append(f"血压{r.blood_pressure_systolic}/{r.blood_pressure_diastolic}")
            if r.heart_rate > 0: parts.append(f"心率{r.heart_rate}")
            if r.blood_sugar > 0: parts.append(f"血糖{r.blood_sugar}")
            if len(parts) > 1:
                health_lines.append("，".join(parts))
        health_context = "\n".join(health_lines) if health_lines else "暂无近期健康数据"
        return (
            "当前未配置 AI 模型（LLM_API_KEY 为空）。\n\n"
            f"你的近期健康数据：\n{health_context}\n\n"
            "如需 AI 对话功能，请在后端 .env 中配置 LLM_API_KEY。"
        )

    try:
        # 组装消息历史
        from langchain_core.messages import HumanMessage, AIMessage
        messages = []
        for h in history[-20:]:
            if h.get("role") == "user":
                messages.append(HumanMessage(content=h.get("content", "")))
            elif h.get("role") == "assistant":
                messages.append(AIMessage(content=h.get("content", "")))
        messages.append(HumanMessage(content=message))

        # 运行 Agent 循环（自动执行工具调用）
        return _run_agent_loop(db, user_id, messages)

    except Exception as e:
        logger.exception(f"agent_chat 执行失败: {e}")
        # 回退到简单模式
        return chat_with_advisor(db, user_id, message)
