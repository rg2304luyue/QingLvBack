"""健康数据服务"""
from datetime import date, datetime, timedelta
from sqlalchemy import func, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.health import HealthRecord, WaterIntake, WaterGoal, ReminderPlan, CheckinRecord, WeightGoal, SleepRecord


# ── 健康记录 CRUD ──

def create_health_record(db: Session, user_id: int, data: dict) -> HealthRecord:
    if data.get("timestamp") is None:
        data["timestamp"] = datetime.now()
    record = HealthRecord(user_id=user_id, **data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_health_record(db: Session, user_id: int, record_id: int, data: dict) -> HealthRecord | None:
    record = db.query(HealthRecord).filter(HealthRecord.id == record_id, HealthRecord.user_id == user_id).first()
    if not record:
        return None
    for field, value in data.items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def delete_health_record(db: Session, user_id: int, record_id: int) -> bool:
    result = db.query(HealthRecord).filter(HealthRecord.id == record_id, HealthRecord.user_id == user_id).delete()
    db.commit()
    return result > 0


def get_records(
    db: Session, user_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 100, offset: int = 0,
) -> tuple[list[HealthRecord], int]:
    q = db.query(HealthRecord).filter(HealthRecord.user_id == user_id)
    if start_date:
        q = q.filter(func.date(HealthRecord.timestamp) >= start_date)
    if end_date:
        q = q.filter(func.date(HealthRecord.timestamp) <= end_date)
    total = q.count()
    records = q.order_by(HealthRecord.timestamp.desc()).offset(offset).limit(limit).all()
    return records, total


def get_latest_record(db: Session, user_id: int) -> HealthRecord | None:
    return (
        db.query(HealthRecord)
        .filter(HealthRecord.user_id == user_id)
        .order_by(HealthRecord.timestamp.desc())
        .first()
    )


def get_trend(db: Session, user_id: int, field: str, days: int = 30) -> list[dict]:
    end = datetime.now()
    start = end - timedelta(days=days)
    records = (
        db.query(HealthRecord)
        .filter(HealthRecord.user_id == user_id, HealthRecord.timestamp >= start, HealthRecord.timestamp <= end)
        .order_by(HealthRecord.timestamp.asc())
        .all()
    )
    field_map = {
        "weight": "weight", "bmi": "bmi", "body_fat": "body_fat_percentage",
        "systolic": "blood_pressure_systolic", "diastolic": "blood_pressure_diastolic",
        "heart_rate": "heart_rate", "blood_sugar": "blood_sugar",
    }
    attr = field_map.get(field, "weight")
    return [
        {"date": r.timestamp.strftime("%m/%d"), "value": getattr(r, attr, 0)}
        for r in records if getattr(r, attr, 0) > 0
    ]


# ── 饮水 ──

def get_today_water(db: Session, user_id: int) -> WaterIntake:
    today = date.today()
    record = db.query(WaterIntake).filter(WaterIntake.user_id == user_id, WaterIntake.date == today).first()
    if not record:
        goal_record = db.query(WaterGoal).filter(WaterGoal.user_id == user_id).first()
        daily_goal = goal_record.daily_goal if goal_record else 8
        record = WaterIntake(user_id=user_id, date=today, cup_count=0, daily_goal=daily_goal)
        db.add(record)
        db.commit()
        db.refresh(record)
    return record


def drink_water(db: Session, user_id: int) -> WaterIntake:
    today = date.today()
    # 原子 +1，避免并发竞争
    db.execute(
        update(WaterIntake)
        .where(WaterIntake.user_id == user_id, WaterIntake.date == today, WaterIntake.cup_count < 20)
        .values(cup_count=WaterIntake.cup_count + 1)
    )
    db.commit()
    return get_today_water(db, user_id)


def set_water_goal(db: Session, user_id: int, goal: int) -> WaterIntake:
    goal_value = max(1, goal)
    wg = db.query(WaterGoal).filter(WaterGoal.user_id == user_id).first()
    if wg:
        wg.daily_goal = goal_value
    else:
        wg = WaterGoal(user_id=user_id, daily_goal=goal_value)
        db.add(wg)
    db.commit()
    record = get_today_water(db, user_id)
    record.daily_goal = goal_value
    db.commit()
    db.refresh(record)
    return record


# ── 提醒计划 ──

def get_plans(db: Session, user_id: int) -> list[ReminderPlan]:
    return db.query(ReminderPlan).filter(ReminderPlan.user_id == user_id).order_by(ReminderPlan.time.asc()).all()


def save_plan(db: Session, user_id: int, data: dict) -> ReminderPlan:
    plan_id = data.get("plan_id")
    existing = db.query(ReminderPlan).filter(
        ReminderPlan.user_id == user_id, ReminderPlan.plan_id == plan_id
    ).first() if plan_id else None
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    plan = ReminderPlan(user_id=user_id, **data)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def delete_plan(db: Session, user_id: int, plan_id: str) -> bool:
    result = db.query(ReminderPlan).filter(
        ReminderPlan.user_id == user_id, ReminderPlan.plan_id == plan_id
    ).delete()
    db.commit()
    return result > 0


# ── 打卡 ──

def checkin(db: Session, user_id: int, plan_id: str) -> CheckinRecord:
    today = date.today()
    existing = db.query(CheckinRecord).filter(
        CheckinRecord.user_id == user_id,
        CheckinRecord.plan_id == plan_id,
        CheckinRecord.checkin_date == today,
    ).first()
    if existing:
        return existing
    record = CheckinRecord(user_id=user_id, plan_id=plan_id, checkin_date=today)
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        record = db.query(CheckinRecord).filter(
            CheckinRecord.user_id == user_id,
            CheckinRecord.plan_id == plan_id,
            CheckinRecord.checkin_date == today,
        ).first()
    return record


def get_checkin_streak(db: Session, user_id: int, plan_id: str) -> int:
    today = date.today()
    # 一次查询获取最近 365 天的所有打卡日期
    start = today - timedelta(days=365)
    dates = sorted(
        db.query(CheckinRecord.checkin_date)
        .filter(
            CheckinRecord.user_id == user_id,
            CheckinRecord.plan_id == plan_id,
            CheckinRecord.checkin_date >= start,
        )
        .all(),
        reverse=True,
    )
    dates = [d[0] for d in dates]
    if not dates or dates[0] != today:
        return 0
    streak = 1
    for i in range(1, len(dates)):
        if dates[i - 1] - dates[i] == timedelta(days=1):
            streak += 1
        else:
            break
    return streak


# ── 体重目标 ──

def get_weight_goal(db: Session, user_id: int) -> WeightGoal | None:
    return db.query(WeightGoal).filter(WeightGoal.user_id == user_id).first()


def save_weight_goal(db: Session, user_id: int, target_weight: float, target_date: date | None) -> WeightGoal:
    wg = db.query(WeightGoal).filter(WeightGoal.user_id == user_id).first()
    if wg:
        wg.target_weight = target_weight
        wg.target_date = target_date
    else:
        wg = WeightGoal(user_id=user_id, target_weight=target_weight, target_date=target_date)
        db.add(wg)
    db.commit()
    db.refresh(wg)
    return wg


# ── 睡眠记录 ──

def create_sleep_record(db: Session, user_id: int, data: dict) -> SleepRecord:
    today = date.today()
    existing = db.query(SleepRecord).filter(SleepRecord.user_id == user_id, SleepRecord.date == today).first()
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    record = SleepRecord(user_id=user_id, date=today, **data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_today_sleep(db: Session, user_id: int) -> SleepRecord | None:
    today = date.today()
    return db.query(SleepRecord).filter(SleepRecord.user_id == user_id, SleepRecord.date == today).first()


def get_sleep_history(db: Session, user_id: int, days: int = 7) -> list[SleepRecord]:
    start = date.today() - timedelta(days=days)
    return (
        db.query(SleepRecord)
        .filter(SleepRecord.user_id == user_id, SleepRecord.date >= start)
        .order_by(SleepRecord.date.asc())
        .all()
    )
