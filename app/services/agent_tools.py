"""
Agent Tools：供 LangGraph Agent 调用的工具函数
每个 tool 接收一个字符串参数，返回字符串结果
通过闭包绑定 db 和 user_id
"""
import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def create_tools(db: Session, user_id: int) -> list:
    """
    创建绑定好 db 和 user_id 的工具列表
    返回 LangChain Tool 对象列表
    """
    from langchain_core.tools import tool

    # ── 内部数据查询函数 ──

    def _get_user():
        from app.models.user import User
        return db.query(User).filter(User.id == user_id).first()

    def _get_records(days: int = 30):
        from app.models.health import HealthRecord
        start = datetime.now() - timedelta(days=days)
        return (
            db.query(HealthRecord)
            .filter(HealthRecord.user_id == user_id, HealthRecord.timestamp >= start)
            .order_by(HealthRecord.timestamp.desc())
            .all()
        )

    def _format_record(r) -> dict:
        """将 ORM 对象转为字典"""
        d = {}
        d["date"] = r.timestamp.strftime("%Y-%m-%d")
        if r.weight > 0: d["weight"] = r.weight
        if r.bmi > 0: d["bmi"] = round(r.bmi, 1)
        if r.blood_pressure_systolic > 0:
            d["blood_pressure"] = f"{r.blood_pressure_systolic}/{r.blood_pressure_diastolic}"
        if r.heart_rate > 0: d["heart_rate"] = r.heart_rate
        if r.blood_sugar > 0: d["blood_sugar"] = r.blood_sugar
        if r.step_count > 0: d["step_count"] = r.step_count
        if r.sleep_hours > 0: d["sleep_hours"] = round(r.sleep_hours, 1)
        if r.waist_circumference > 0: d["waist"] = r.waist_circumference
        if r.hip_circumference > 0: d["hip"] = r.hip_circumference
        if r.body_fat_percentage > 0: d["body_fat"] = round(r.body_fat_percentage, 1)
        return d

    # ── 工具定义 ──

    @tool
    def get_user_profile() -> str:
        """获取用户个人信息（身高、体重、性别、年龄、BMI）。当用户询问个人身体信息时使用。"""
        user = _get_user()
        if not user:
            return "未找到用户信息"
        profile = {}
        if user.nick_name: profile["nick_name"] = user.nick_name
        if user.gender: profile["gender"] = user.gender
        if user.height > 0: profile["height_cm"] = user.height
        if user.weight > 0: profile["weight_kg"] = user.weight
        if user.birthday:
            age = int((datetime.now().date() - user.birthday).days / 365.25)
            profile["age"] = age
            profile["birthday"] = user.birthday.strftime("%Y-%m-%d")
        if user.height > 0 and user.weight > 0:
            bmi = round(user.weight / ((user.height / 100) ** 2), 1)
            profile["bmi"] = bmi
            if bmi < 18.5: profile["bmi_level"] = "偏瘦"
            elif bmi < 24: profile["bmi_level"] = "正常"
            elif bmi < 28: profile["bmi_level"] = "偏胖"
            else: profile["bmi_level"] = "肥胖"
        return json.dumps(profile, ensure_ascii=False)

    @tool
    def get_health_records(days: str) -> str:
        """获取最近N天的健康数据记录。参数 days 为天数字符串（如 '7'、'30'、'60'）。
        返回每天的体重、血压、心率、血糖、步数、睡眠等数据。当用户询问历史数据、趋势时使用。"""
        try:
            n = int(days)
        except ValueError:
            n = 7
        n = min(n, 90)
        records = _get_records(n)
        if not records:
            return json.dumps({"message": f"最近{n}天暂无健康数据", "records": []}, ensure_ascii=False)
        data = [_format_record(r) for r in records]
        return json.dumps({"total": len(data), "records": data}, ensure_ascii=False)

    @tool
    def get_today_water_intake() -> str:
        """获取今日饮水数据，包括已喝杯数和目标杯数。当用户询问饮水相关问题时使用。"""
        from app.models.health import WaterIntake
        today = datetime.now().date()
        water = db.query(WaterIntake).filter(
            WaterIntake.user_id == user_id, WaterIntake.date == today
        ).first()
        if not water:
            return json.dumps({"message": "今日暂无饮水记录", "cup_count": 0, "daily_goal": 8}, ensure_ascii=False)
        return json.dumps({
            "cup_count": water.cup_count,
            "daily_goal": water.daily_goal,
            "remaining": max(0, water.daily_goal - water.cup_count),
            "progress_percent": round(water.cup_count / max(water.daily_goal, 1) * 100, 1),
        }, ensure_ascii=False)

    @tool
    def get_weight_goal() -> str:
        """获取用户的体重目标（目标体重和目标日期）。当用户询问减重目标、进度时使用。"""
        from app.models.health import WeightGoal
        goal = db.query(WeightGoal).filter(WeightGoal.user_id == user_id).first()
        if not goal or goal.target_weight <= 0:
            return json.dumps({"message": "未设定体重目标"}, ensure_ascii=False)
        user = _get_user()
        current_weight = user.weight if user and user.weight > 0 else 0
        result = {
            "target_weight": goal.target_weight,
            "current_weight": current_weight,
        }
        if goal.target_date:
            result["target_date"] = goal.target_date.strftime("%Y-%m-%d")
            days_left = (goal.target_date - datetime.now().date()).days
            result["days_remaining"] = max(0, days_left)
        if current_weight > 0:
            diff = current_weight - goal.target_weight
            result["weight_to_lose"] = round(diff, 1)
            result["direction"] = "需要减重" if diff > 0 else "已达标" if abs(diff) < 0.5 else "需要增重"
        return json.dumps(result, ensure_ascii=False)

    @tool
    def get_checkin_streak() -> str:
        """获取用户的打卡记录和连续打卡天数。当用户询问打卡习惯、坚持天数时使用。"""
        from app.models.health import CheckinRecord
        records = (
            db.query(CheckinRecord)
            .filter(CheckinRecord.user_id == user_id)
            .order_by(CheckinRecord.checkin_date.desc())
            .limit(60)
            .all()
        )
        if not records:
            return json.dumps({"message": "暂无打卡记录", "total_days": 0, "current_streak": 0}, ensure_ascii=False)
        # 计算连续打卡天数
        dates = sorted([r.checkin_date for r in records], reverse=True)
        streak = 0
        today = datetime.now().date()
        for i, d in enumerate(dates):
            expected = today - timedelta(days=i)
            if d == expected:
                streak += 1
            else:
                break
        return json.dumps({
            "total_checkin_days": len(set(dates)),
            "current_streak": streak,
            "recent_dates": [d.strftime("%m/%d") for d in dates[:10]],
        }, ensure_ascii=False)

    @tool
    def get_favorite_articles() -> str:
        """获取用户收藏的健康知识文章列表。当用户询问收藏内容、健康知识时使用。"""
        from app.models.knowledge import KnowledgeArticle, KnowledgeFavorite
        fav_ids = [
            r[0] for r in db.query(KnowledgeFavorite.article_id)
            .filter(KnowledgeFavorite.user_id == user_id).all()
        ]
        if not fav_ids:
            return json.dumps({"message": "暂无收藏文章", "articles": []}, ensure_ascii=False)
        articles = (
            db.query(KnowledgeArticle)
            .filter(KnowledgeArticle.id.in_(fav_ids))
            .order_by(KnowledgeArticle.sort_order.asc())
            .limit(10).all()
        )
        data = [{"title": a.title, "tag": a.tag, "summary": a.sub_title} for a in articles]
        return json.dumps({"total": len(data), "articles": data}, ensure_ascii=False)

    @tool
    def analyze_nutrition(food_description: str) -> str:
        """分析食物的营养成分和热量。参数为食物描述（如'一碗米饭配鸡胸肉和西兰花'）。
        当用户询问饮食营养、热量计算、食物搭配时使用。
        返回估算的热量、蛋白质、碳水、脂肪等信息。"""
        # 常见食物营养数据库（每100g）
        food_db = {
            "米饭": {"calories": 116, "protein": 2.6, "carbs": 25.9, "fat": 0.3, "portion": 150},
            "面条": {"calories": 110, "protein": 3.5, "carbs": 22, "fat": 0.5, "portion": 200},
            "馒头": {"calories": 221, "protein": 7.0, "carbs": 47, "fat": 1.1, "portion": 100},
            "鸡胸肉": {"calories": 133, "protein": 31, "carbs": 0, "fat": 1.2, "portion": 150},
            "鸡蛋": {"calories": 144, "protein": 13.3, "carbs": 1.5, "fat": 8.8, "portion": 60},
            "牛肉": {"calories": 125, "protein": 26, "carbs": 0, "fat": 2.5, "portion": 150},
            "猪肉": {"calories": 242, "protein": 13.2, "carbs": 1.5, "fat": 20, "portion": 100},
            "鱼": {"calories": 104, "protein": 18, "carbs": 0, "fat": 3.2, "portion": 200},
            "虾": {"calories": 87, "protein": 18, "carbs": 0, "fat": 1.2, "portion": 150},
            "西兰花": {"calories": 34, "protein": 4.1, "carbs": 4.3, "fat": 0.6, "portion": 150},
            "菠菜": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "portion": 100},
            "番茄": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "portion": 150},
            "黄瓜": {"calories": 15, "protein": 0.7, "carbs": 2.9, "fat": 0.1, "portion": 200},
            "苹果": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "portion": 200},
            "香蕉": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3, "portion": 120},
            "牛奶": {"calories": 42, "protein": 3.4, "carbs": 5, "fat": 1, "portion": 250},
            "酸奶": {"calories": 72, "protein": 3.6, "carbs": 9.3, "fat": 2.7, "portion": 200},
            "豆腐": {"calories": 76, "protein": 8.1, "carbs": 2.8, "fat": 3.7, "portion": 150},
            "红薯": {"calories": 86, "protein": 1.6, "carbs": 20, "fat": 0.1, "portion": 200},
            "玉米": {"calories": 112, "protein": 4, "carbs": 22, "fat": 1.2, "portion": 200},
            "沙拉": {"calories": 20, "protein": 1.5, "carbs": 3, "fat": 0.2, "portion": 200},
        }

        matched = []
        total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

        for name, info in food_db.items():
            if name in food_description:
                portion = info["portion"]
                factor = portion / 100
                item = {
                    "food": name,
                    "portion_g": portion,
                    "calories": round(info["calories"] * factor),
                    "protein": round(info["protein"] * factor, 1),
                    "carbs": round(info["carbs"] * factor, 1),
                    "fat": round(info["fat"] * factor, 1),
                }
                matched.append(item)
                for k in ["calories", "protein", "carbs", "fat"]:
                    total[k] += item[k]

        if not matched:
            return json.dumps({
                "message": f"未能识别食物'{food_description}'中的具体食材，请尝试更详细的描述（如'米饭配鸡胸肉'）",
                "foods": [], "total": {},
            }, ensure_ascii=False)

        result = {
            "foods": matched,
            "total": {k: round(v, 1) for k, v in total.items()},
            "meal_calories": round(total["calories"]),
            "daily_target_calories": 2000,
            "meal_percent_of_daily": round(total["calories"] / 2000 * 100, 1),
        }
        return json.dumps(result, ensure_ascii=False)

    @tool
    def generate_exercise_plan(goal: str) -> str:
        """根据用户身体状况和目标生成运动计划。参数 goal 描述运动目标（如'减重'、'增肌'、'改善心肺'、'保持健康'）。
        当用户询问运动建议、锻炼计划时使用。"""
        user = _get_user()
        bmi = 0
        if user and user.height > 0 and user.weight > 0:
            bmi = user.weight / ((user.height / 100) ** 2)

        # 根据 BMI 和目标推荐运动
        plans = {
            "减重": {
                "focus": "有氧运动为主 + 适量力量训练",
                "weekly_plan": [
                    {"day": "周一", "activity": "快走/慢跑 40分钟", "intensity": "中等"},
                    {"day": "周二", "activity": "上肢力量训练 30分钟", "intensity": "中等"},
                    {"day": "周三", "activity": "游泳/骑车 45分钟", "intensity": "中等偏高"},
                    {"day": "周四", "activity": "休息或轻度拉伸", "intensity": "低"},
                    {"day": "周五", "activity": "下肢力量训练 30分钟", "intensity": "中等"},
                    {"day": "周六", "activity": "HIIT间歇训练 25分钟", "intensity": "高"},
                    {"day": "周日", "activity": "户外散步/瑜伽 40分钟", "intensity": "低"},
                ],
                "tips": ["每周运动4-5次，每次30-60分钟", "有氧运动心率保持在最大心率的60-70%", "配合饮食控制效果更佳"],
            },
            "增肌": {
                "focus": "力量训练为主 + 充足蛋白质",
                "weekly_plan": [
                    {"day": "周一", "activity": "胸+三头肌力量训练 50分钟", "intensity": "高"},
                    {"day": "周二", "activity": "背+二头肌力量训练 50分钟", "intensity": "高"},
                    {"day": "周三", "activity": "有氧恢复 30分钟（慢跑/游泳）", "intensity": "低"},
                    {"day": "周四", "activity": "肩+核心训练 50分钟", "intensity": "高"},
                    {"day": "周五", "activity": "腿部力量训练 50分钟", "intensity": "高"},
                    {"day": "周六", "activity": "全身拉伸+瑜伽 40分钟", "intensity": "低"},
                    {"day": "周日", "activity": "休息日", "intensity": "无"},
                ],
                "tips": ["每组动作8-12次，做3-4组", "训练后30分钟内补充蛋白质", "保证每天睡眠7-8小时"],
            },
            "改善心肺": {
                "focus": "有氧运动 + 循序渐进",
                "weekly_plan": [
                    {"day": "周一", "activity": "快走 30分钟", "intensity": "低"},
                    {"day": "周二", "activity": "跳绳 20分钟（间歇式）", "intensity": "中等"},
                    {"day": "周三", "activity": "休息", "intensity": "无"},
                    {"day": "周四", "activity": "骑车 35分钟", "intensity": "中等"},
                    {"day": "周五", "activity": "游泳 30分钟", "intensity": "中等"},
                    {"day": "周六", "activity": "慢跑 25分钟", "intensity": "中等"},
                    {"day": "周日", "activity": "户外散步 40分钟", "intensity": "低"},
                ],
                "tips": ["运动时心率控制在最大心率的50-70%", "最大心率 ≈ 220 - 年龄", "感到不适应立即停止"],
            },
        }

        plan = plans.get(goal, plans["减重"])
        result = {
            "goal": goal,
            "user_bmi": round(bmi, 1) if bmi > 0 else "未知",
            "focus": plan["focus"],
            "weekly_plan": plan["weekly_plan"],
            "tips": plan["tips"],
            "note": "请根据自身情况调整运动强度，运动前做好热身。如有心血管疾病请先咨询医生。",
        }
        return json.dumps(result, ensure_ascii=False)

    @tool
    def predict_health_trend(indicator: str) -> str:
        """预测健康指标的未来趋势。参数 indicator 为指标名称（如'weight'、'blood_pressure'、'heart_rate'）。
        基于最近30天数据，预测未来7天的变化趋势。当用户询问趋势、预测时使用。"""
        records = _get_records(30)
        if len(records) < 7:
            return json.dumps({"message": f"数据不足，需要至少7天数据才能预测趋势", "indicator": indicator}, ensure_ascii=False)

        # 提取指标数据
        values = []
        dates = []
        for r in reversed(records):  # 从旧到新
            val = None
            if indicator in ("weight", "体重"):
                val = r.weight if r.weight > 0 else None
            elif indicator in ("heart_rate", "心率"):
                val = r.heart_rate if r.heart_rate > 0 else None
            elif indicator in ("blood_sugar", "血糖"):
                val = r.blood_sugar if r.blood_sugar > 0 else None
            elif indicator in ("blood_pressure", "血压"):
                val = r.blood_pressure_systolic if r.blood_pressure_systolic > 0 else None
            elif indicator in ("bmi", "BMI"):
                val = r.bmi if r.bmi > 0 else None
            else:
                val = r.weight if r.weight > 0 else None

            if val is not None:
                values.append(val)
                dates.append(r.timestamp.strftime("%m/%d"))

        if len(values) < 3:
            return json.dumps({"message": f"'{indicator}'数据不足", "data_points": len(values)}, ensure_ascii=False)

        # 简单线性趋势预测
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean

        # 预测未来7天
        predictions = []
        for i in range(1, 8):
            predicted = slope * (n - 1 + i) + intercept
            predictions.append({
                "day": f"+{i}天",
                "value": round(predicted, 1),
                "date": (datetime.now() + timedelta(days=i)).strftime("%m/%d"),
            })

        # 趋势判断
        if abs(slope) < 0.05:
            trend = "基本稳定"
        elif slope > 0:
            trend = "呈上升趋势" if indicator in ("weight", "体重", "bmi") else "呈上升趋势"
        else:
            trend = "呈下降趋势" if indicator in ("weight", "体重", "bmi") else "呈下降趋势"

        result = {
            "indicator": indicator,
            "data_points": n,
            "latest_value": values[-1],
            "avg_value": round(y_mean, 1),
            "min_value": round(min(values), 1),
            "max_value": round(max(values), 1),
            "trend": trend,
            "daily_change": round(slope, 2),
            "predictions": predictions,
            "recent_data": [{"date": dates[i], "value": values[i]} for i in range(max(0, n - 7), n)],
        }
        return json.dumps(result, ensure_ascii=False)

    @tool
    def assess_health_risk() -> str:
        """综合评估用户的健康风险等级。基于最近30天数据，评估各项指标的风险。
        当用户询问健康状况、风险评估、需要注意什么时使用。"""
        user = _get_user()
        records = _get_records(30)
        if not records:
            return json.dumps({"message": "暂无健康数据，无法评估风险"}, ensure_ascii=False)

        latest = records[0]
        risks = []
        score = 100

        # BMI 风险
        if user and user.height > 0 and user.weight > 0:
            bmi = user.weight / ((user.height / 100) ** 2)
            if bmi >= 28:
                risks.append({"indicator": "BMI", "level": "高", "value": round(bmi, 1), "advice": "建议制定减重计划，控制饮食热量"})
                score -= 20
            elif bmi >= 24:
                risks.append({"indicator": "BMI", "level": "中", "value": round(bmi, 1), "advice": "建议适当控制饮食，增加运动"})
                score -= 10
            elif bmi < 18.5:
                risks.append({"indicator": "BMI", "level": "中", "value": round(bmi, 1), "advice": "建议增加营养摄入"})
                score -= 10

        # 血压风险
        if latest.blood_pressure_systolic > 0:
            sys_v = latest.blood_pressure_systolic
            dia_v = latest.blood_pressure_diastolic
            if sys_v >= 140 or dia_v >= 90:
                risks.append({"indicator": "血压", "level": "高", "value": f"{sys_v}/{dia_v}", "advice": "建议就医，低盐饮食，定期监测"})
                score -= 20
            elif sys_v >= 130 or dia_v >= 85:
                risks.append({"indicator": "血压", "level": "中", "value": f"{sys_v}/{dia_v}", "advice": "注意低盐饮食，减少压力"})
                score -= 10

        # 血糖风险
        if latest.blood_sugar > 0:
            bs = latest.blood_sugar
            if bs > 7.0:
                risks.append({"indicator": "血糖", "level": "高", "value": bs, "advice": "建议就医检查，控制碳水摄入"})
                score -= 20
            elif bs > 6.1:
                risks.append({"indicator": "血糖", "level": "中", "value": bs, "advice": "注意饮食控制，减少糖分摄入"})
                score -= 10

        # 心率风险
        if latest.heart_rate > 0:
            hr = latest.heart_rate
            if hr > 100 or hr < 50:
                risks.append({"indicator": "心率", "level": "中", "value": hr, "advice": "建议关注心率变化，必要时就医"})
                score -= 10

        # 睡眠风险
        if latest.sleep_hours > 0:
            if latest.sleep_hours < 6:
                risks.append({"indicator": "睡眠", "level": "中", "value": f"{latest.sleep_hours}h", "advice": "建议保证7-8小时睡眠"})
                score -= 10

        score = max(0, score)
        if score >= 90: level = "优秀"
        elif score >= 75: level = "良好"
        elif score >= 60: level = "一般"
        else: level = "需要关注"

        result = {
            "score": score,
            "level": level,
            "risk_count": len(risks),
            "risks": risks if risks else [{"indicator": "总体", "level": "低", "value": "各项指标正常", "advice": "继续保持良好的生活习惯"}],
            "summary": f"健康评分 {score}/100（{level}），发现 {len(risks)} 项需要关注。" if risks else f"健康评分 {score}/100（{level}），各项指标正常，继续保持！",
        }
        return json.dumps(result, ensure_ascii=False)

    # 返回工具列表
    return [
        get_user_profile,
        get_health_records,
        get_today_water_intake,
        get_weight_goal,
        get_checkin_streak,
        get_favorite_articles,
        analyze_nutrition,
        generate_exercise_plan,
        predict_health_trend,
        assess_health_risk,
    ]
