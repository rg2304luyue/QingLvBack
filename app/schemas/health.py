"""健康数据 Schema"""
from datetime import date, datetime
from pydantic import BaseModel, Field


# ── 体重目标 ──

class WeightGoalCreate(BaseModel):
    target_weight: float = 0
    target_date: date | None = None


class WeightGoalResponse(BaseModel):
    target_weight: float
    target_date: date | None

    class Config:
        from_attributes = True


# ── 睡眠记录 ──

class SleepRecordCreate(BaseModel):
    sleep_hours: float = 0
    deep_sleep_hours: float = 0
    light_sleep_hours: float = 0
    bed_time: str = "23:00"
    wake_time: str = "07:00"
    quality_score: int = 0


class SleepRecordResponse(BaseModel):
    id: int
    date: date
    sleep_hours: float
    deep_sleep_hours: float
    light_sleep_hours: float
    bed_time: str
    wake_time: str
    quality_score: int

    class Config:
        from_attributes = True


# ── 健康记录 ──

class HealthRecordCreate(BaseModel):
    weight: float = 0
    bmi: float = 0
    body_fat_percentage: float = 0
    fat_weight: float = 0
    blood_sugar: float = 0
    blood_pressure_systolic: int = 0
    blood_pressure_diastolic: int = 0
    heart_rate: int = 0
    waist_circumference: float = 0
    hip_circumference: float = 0
    step_count: int = 0
    sleep_hours: float = 0
    timestamp: datetime | None = None


class HealthRecordResponse(BaseModel):
    id: int
    timestamp: datetime
    weight: float
    bmi: float
    body_fat_percentage: float
    fat_weight: float
    blood_sugar: float
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: int
    waist_circumference: float
    hip_circumference: float
    step_count: int
    sleep_hours: float

    class Config:
        from_attributes = True


class HealthRecordListResponse(BaseModel):
    total: int
    records: list[HealthRecordResponse]


# ── 仪表盘 ──

class DashboardResponse(BaseModel):
    today_score: int
    score_level: str
    bmi: float
    bmi_level: str
    weight: float
    body_fat_percentage: float
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: int
    blood_sugar: float
    step_count: int
    sleep_hours: float
    water_cups: int
    water_goal: int


# ── 趋势 ──

class TrendPoint(BaseModel):
    date: str
    value: float


class TrendResponse(BaseModel):
    metric: str
    unit: str
    points: list[TrendPoint]


# ── 饮水 ──

class WaterIntakeResponse(BaseModel):
    date: date
    cup_count: int
    daily_goal: int

    class Config:
        from_attributes = True


# ── 提醒计划 ──

class ReminderPlanCreate(BaseModel):
    plan_id: str
    plan_type: int = 0
    name: str
    time: str
    dosage: str = ""
    is_enabled: bool = True


class ReminderPlanResponse(BaseModel):
    id: int
    plan_id: str
    plan_type: int
    name: str
    time: str
    dosage: str
    is_enabled: bool

    class Config:
        from_attributes = True
