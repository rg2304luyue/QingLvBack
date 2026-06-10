"""清律健康 App 后端入口"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.routers import auth, health, analysis, knowledge, chat
from app.services.mock_generator import backfill_data

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：建表 + 创建 demo 用户 + 回填 30 天数据
    Base.metadata.create_all(bind=engine)

    if settings.mock_data_enabled:
        try:
            db = SessionLocal()
            from app.models.user import User
            from app.services.auth_service import hash_password
            demo = db.query(User).filter(User.username == "demo").first()
            if not demo:
                demo = User(
                    username="demo", password_hash=hash_password("demo123"),
                    nick_name="健康用户", gender="男", height=172, weight=68,
                )
                db.add(demo)
                db.commit()
                db.refresh(demo)
            backfill_data(db, demo.id, days=30)
            db.close()

            from apscheduler.schedulers.background import BackgroundScheduler
            from app.services.mock_generator import daily_job
            scheduler = BackgroundScheduler()
            scheduler.add_job(lambda: daily_job(SessionLocal), trigger="cron", hour=1, minute=0, id="daily_mock")
            scheduler.start()
        except Exception as e:
            logger.warning(f"启动初始化跳过（数据库可能未就绪）: {e}")

    yield


app = FastAPI(
    title="清律健康 API",
    description="健康数据管理 + AI 分析后端",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # 通配符来源不能同时开启 credentials
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(knowledge.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"app": "清律健康 API", "version": "1.0.0", "docs": "/docs"}
