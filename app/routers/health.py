"""健康数据路由：CRUD + 仪表盘 + 趋势 + 饮水 + 提醒"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.health import (
    HealthRecordCreate, HealthRecordResponse, HealthRecordListResponse,
    DashboardResponse, TrendResponse, TrendPoint,
    WaterIntakeResponse, ReminderPlanCreate, ReminderPlanResponse,
)
from app.services import health_service

router = APIRouter(prefix="/api/health", tags=["健康数据"])


def _bmi_level(bmi: float) -> str:
    if bmi <= 0: return "无数据"
    if bmi < 18.5: return "偏瘦"
    if bmi < 24: return "正常"
    if bmi < 28: return "偏胖"
    return "肥胖"


# ── 健康记录 CRUD ──

@router.post("/records", response_model=HealthRecordResponse)
def add_record(body: HealthRecordCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = health_service.create_health_record(db, current_user.id, body.model_dump())
    return HealthRecordResponse.model_validate(record)


@router.get("/records", response_model=HealthRecordListResponse)
def list_records(
    start_date: date | None = Query(None), end_date: date | None = Query(None),
    limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    records, total = health_service.get_records(db, current_user.id, start_date, end_date, limit, offset)
    return HealthRecordListResponse(total=total, records=[HealthRecordResponse.model_validate(r) for r in records])


# ── 仪表盘 ──

@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.ai_analysis import _rule_based_analysis
    latest = health_service.get_latest_record(db, current_user.id)
    water = health_service.get_today_water(db, current_user.id)
    analysis = _rule_based_analysis(db, current_user.id)

    if latest:
        return DashboardResponse(
            today_score=analysis["overall_score"], score_level=analysis["score_level"],
            bmi=round(latest.bmi, 1), bmi_level=_bmi_level(latest.bmi),
            weight=latest.weight, body_fat_percentage=round(latest.body_fat_percentage, 1),
            blood_pressure_systolic=latest.blood_pressure_systolic,
            blood_pressure_diastolic=latest.blood_pressure_diastolic,
            heart_rate=latest.heart_rate, blood_sugar=round(latest.blood_sugar, 1),
            step_count=latest.step_count, sleep_hours=round(latest.sleep_hours, 1),
            water_cups=water.cup_count, water_goal=water.daily_goal,
        )
    return DashboardResponse(
        today_score=0, score_level="无数据", bmi=0, bmi_level="无数据",
        weight=0, body_fat_percentage=0, blood_pressure_systolic=0,
        blood_pressure_diastolic=0, heart_rate=0, blood_sugar=0,
        step_count=0, sleep_hours=0, water_cups=0, water_goal=8,
    )


# ── 趋势 ──

@router.get("/trends/{field}", response_model=TrendResponse)
def get_trend(
    field: str, days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    valid = {"weight", "bmi", "body_fat", "systolic", "diastolic", "heart_rate", "blood_sugar"}
    if field not in valid:
        field = "weight"
    unit_map = {"weight": "斤", "bmi": "", "body_fat": "%", "systolic": "mmHg", "diastolic": "mmHg", "heart_rate": "次/分", "blood_sugar": "mmol/L"}
    points = health_service.get_trend(db, current_user.id, field, days)
    return TrendResponse(metric=field, unit=unit_map.get(field, ""), points=[TrendPoint(**p) for p in points])


# ── 饮水 ──

@router.get("/water", response_model=WaterIntakeResponse)
def get_water(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WaterIntakeResponse.model_validate(health_service.get_today_water(db, current_user.id))


@router.post("/water/drink", response_model=WaterIntakeResponse)
def drink_water(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WaterIntakeResponse.model_validate(health_service.drink_water(db, current_user.id))


@router.put("/water/goal", response_model=WaterIntakeResponse)
def set_water_goal(goal: int = Query(..., ge=1, le=20), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WaterIntakeResponse.model_validate(health_service.set_water_goal(db, current_user.id, goal))


# ── 提醒计划 ──

@router.get("/plans", response_model=list[ReminderPlanResponse])
def list_plans(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [ReminderPlanResponse.model_validate(p) for p in health_service.get_plans(db, current_user.id)]


@router.post("/plans", response_model=ReminderPlanResponse)
def create_plan(body: ReminderPlanCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReminderPlanResponse.model_validate(health_service.save_plan(db, current_user.id, body.model_dump()))


@router.delete("/plans/{plan_id}")
def remove_plan(plan_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not health_service.delete_plan(db, current_user.id, plan_id):
        raise HTTPException(status_code=404, detail="计划不存在")
    return {"message": "已删除"}


@router.post("/checkin/{plan_id}")
def checkin_plan(plan_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = health_service.checkin(db, current_user.id, plan_id)
    streak = health_service.get_checkin_streak(db, current_user.id, plan_id)
    return {"plan_id": plan_id, "checkin_date": str(record.checkin_date), "streak": streak}
