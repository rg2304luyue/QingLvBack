"""健康数据相关模型"""
from sqlalchemy import (
    Column, Integer, Float, String, Date, DateTime,
    ForeignKey, Boolean, func,
)
from app.database import Base


class HealthRecord(Base):
    """健康数据记录 —— 对应 App 的 HealthDataRecord"""
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    weight = Column(Float, default=0)                       # 斤
    bmi = Column(Float, default=0)
    body_fat_percentage = Column(Float, default=0)          # %
    fat_weight = Column(Float, default=0)
    blood_sugar = Column(Float, default=0)                  # mmol/L
    blood_pressure_systolic = Column(Integer, default=0)    # 收缩压
    blood_pressure_diastolic = Column(Integer, default=0)   # 舒张压
    heart_rate = Column(Integer, default=0)                 # 次/分
    waist_circumference = Column(Float, default=0)
    hip_circumference = Column(Float, default=0)
    step_count = Column(Integer, default=0)
    sleep_hours = Column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())


class WaterIntake(Base):
    """每日饮水记录"""
    __tablename__ = "water_intake"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    cup_count = Column(Integer, default=0)
    daily_goal = Column(Integer, default=8)


class ReminderPlan(Base):
    """提醒计划"""
    __tablename__ = "reminder_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(String(64), nullable=False)
    plan_type = Column(Integer, default=0)   # 0=饮水 1=用药
    name = Column(String(64), default="")
    time = Column(String(8), default="08:00")
    dosage = Column(String(32), default="")
    is_enabled = Column(Boolean, default=True)


class CheckinRecord(Base):
    """打卡记录"""
    __tablename__ = "checkin_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(String(64), nullable=False)
    checkin_date = Column(Date, nullable=False)
