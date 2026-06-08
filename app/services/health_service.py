"""健康数据服务"""
from datetime import date, datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.health import HealthRecord, WaterIntake, ReminderPlan, CheckinRecord


# ── 健康记录 ──

def create_health_record(db: Session, user_id: int, data: dict) -> HealthRecord:
    if data.get("timestamp") is None:
        data["timestamp"] = datetime.now()
    record = HealthRecord(user_id=user_id, **data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


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
        record = WaterIntake(user_id=user_id, date=today, cup_count=0, daily_goal=8)
        db.add(record)
        db.commit()
        db.refresh(record)
    return record


def drink_water(db: Session, user_id: int) -> WaterIntake:
    record = get_today_water(db, user_id)
    if record.cup_count < 20:
        record.cup_count += 1
        db.commit()
        db.refresh(record)
    return record


def set_water_goal(db: Session, user_id: int, goal: int) -> WaterIntake:
    record = get_today_water(db, user_id)
    record.daily_goal = max(1, goal)
    db.commit()
    db.refresh(record)
    return record


# ── 提醒计划 ──

def get_plans(db: Session, user_id: int) -> list[ReminderPlan]:
    return db.query(ReminderPlan).filter(ReminderPlan.user_id == user_id).order_by(ReminderPlan.time.asc()).all()


def save_plan(db: Session, user_id: int, data: dict) -> ReminderPlan:
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
    db.commit()
    db.refresh(record)
    return record


def get_checkin_streak(db: Session, user_id: int, plan_id: str) -> int:
    today = date.today()
    streak = 0
    for i in range(365):
        check_date = today - timedelta(days=i)
        record = db.query(CheckinRecord).filter(
            CheckinRecord.user_id == user_id,
            CheckinRecord.plan_id == plan_id,
            CheckinRecord.checkin_date == check_date,
        ).first()
        if record:
            streak += 1
        else:
            break
    return streak
