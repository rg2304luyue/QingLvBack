"""健康数据相关模型"""
from sqlalchemy import (
    Column, Integer, Float, String, Date, DateTime,
    ForeignKey, Boolean, UniqueConstraint, func,
)
from app.database import Base


class HealthRecord(Base):
    """健康数据记录 —— 对应 App 的 HealthDataRecord"""
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    weight = Column(Float, default=0)
    bmi = Column(Float, default=0)
    body_fat_percentage = Column(Float, default=0)
    fat_weight = Column(Float, default=0)
    blood_sugar = Column(Float, default=0)
    blood_pressure_systolic = Column(Integer, default=0)
    blood_pressure_diastolic = Column(Integer, default=0)
    heart_rate = Column(Integer, default=0)
    waist_circumference = Column(Float, default=0)
    hip_circumference = Column(Float, default=0)
    step_count = Column(Integer, default=0)
    sleep_hours = Column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())


class WaterIntake(Base):
    """每日饮水记录"""
    __tablename__ = "water_intake"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_water_user_date"),)

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
    plan_type = Column(Integer, default=0)
    name = Column(String(64), default="")
    time = Column(String(8), default="08:00")
    dosage = Column(String(32), default="")
    is_enabled = Column(Boolean, default=True)


class CheckinRecord(Base):
    """打卡记录"""
    __tablename__ = "checkin_records"
    __table_args__ = (UniqueConstraint("user_id", "plan_id", "checkin_date", name="uq_checkin_user_plan_date"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(String(64), nullable=False)
    checkin_date = Column(Date, nullable=False)


class WeightGoal(Base):
    """用户体重目标"""
    __tablename__ = "weight_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    target_weight = Column(Float, default=0)
    target_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class WaterGoal(Base):
    """用户饮水目标（全局持久化，不按天重置）"""
    __tablename__ = "water_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    daily_goal = Column(Integer, default=8)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SleepRecord(Base):
    """每日睡眠记录"""
    __tablename__ = "sleep_records"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_sleep_user_date"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    sleep_hours = Column(Float, default=0)
    deep_sleep_hours = Column(Float, default=0)
    light_sleep_hours = Column(Float, default=0)
    bed_time = Column(String(8), default="23:00")
    wake_time = Column(String(8), default="07:00")
    quality_score = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
