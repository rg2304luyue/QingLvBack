"""模拟数据生成器：每天自动生成健康数据 + 饮水数据"""
import random
from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.health import HealthRecord, WaterIntake


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def generate_health_record(user_id: int, target_date: date | None = None) -> dict:
    """基于日期生成一条合理波动的健康数据（同一天结果稳定）"""
    if target_date is None:
        target_date = date.today()

    day_seed = target_date.toordinal()
    rng = random.Random(day_seed)

    base_weight = 70.0
    trend_loss = day_seed * 0.008      # 每天微降 8g
    noise = rng.gauss(0, 0.3)

    weight = _clamp(base_weight - trend_loss + noise, 60, 75)
    bmi = _clamp(weight / (1.72 ** 2), 20, 27)
    body_fat = _clamp(bmi * 1.1 + rng.gauss(0, 0.5), 15, 30)
    fat_weight = _clamp(weight * body_fat / 100, 8, 25)
    blood_sugar = _clamp(4.8 + rng.gauss(0, 0.3), 3.9, 7.0)
    systolic = _clamp(115 + rng.gauss(0, 4), 100, 135)
    diastolic = _clamp(75 + rng.gauss(0, 3), 60, 88)
    heart_rate = _clamp(68 + rng.gauss(0, 5), 55, 90)
    step_count = rng.randint(3000, 12000)
    sleep_hours = _clamp(7 + rng.gauss(0, 0.8), 4, 10)

    return {
        "timestamp": datetime(target_date.year, target_date.month, target_date.day, 8, 0, 0),
        "weight": round(weight * 2, 1),           # 斤
        "bmi": round(bmi, 1),
        "body_fat_percentage": round(body_fat, 1),
        "fat_weight": round(fat_weight, 1),
        "blood_sugar": round(blood_sugar, 1),
        "blood_pressure_systolic": int(systolic),
        "blood_pressure_diastolic": int(diastolic),
        "heart_rate": int(heart_rate),
        "waist_circumference": round(_clamp(80 + rng.gauss(0, 1), 72, 90), 1),
        "hip_circumference": round(_clamp(95 + rng.gauss(0, 1), 88, 102), 1),
        "step_count": step_count,
        "sleep_hours": round(sleep_hours, 1),
    }


def generate_water_intake(user_id: int, target_date: date | None = None) -> dict:
    if target_date is None:
        target_date = date.today()
    rng = random.Random(target_date.toordinal())
    return {"date": target_date, "cup_count": rng.randint(3, 10), "daily_goal": 8}


def backfill_data(db: Session, user_id: int, days: int = 30):
    """回填过去 N 天的模拟数据（跳过已有数据的日期）"""
    today = date.today()
    for i in range(days, 0, -1):
        target = today - timedelta(days=i)

        existing = db.query(HealthRecord).filter(
            HealthRecord.user_id == user_id,
            func.date(HealthRecord.timestamp) == target,
        ).first()
        if not existing:
            db.add(HealthRecord(user_id=user_id, **generate_health_record(user_id, target)))

        water_existing = db.query(WaterIntake).filter(
            WaterIntake.user_id == user_id, WaterIntake.date == target
        ).first()
        if not water_existing:
            db.add(WaterIntake(user_id=user_id, **generate_water_intake(user_id, target)))

    db.commit()


def daily_job(db_factory):
    """APScheduler 每日任务：为所有用户生成当日数据"""
    db = db_factory()
    try:
        from app.models.user import User
        users = db.query(User).all()
        today = date.today()
        for user in users:
            if not db.query(HealthRecord).filter(
                HealthRecord.user_id == user.id, func.date(HealthRecord.timestamp) == today
            ).first():
                db.add(HealthRecord(user_id=user.id, **generate_health_record(user.id, today)))

            if not db.query(WaterIntake).filter(
                WaterIntake.user_id == user.id, WaterIntake.date == today
            ).first():
                db.add(WaterIntake(user_id=user.id, **generate_water_intake(user.id, today)))

        db.commit()
    finally:
        db.close()
