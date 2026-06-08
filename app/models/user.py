"""用户表模型"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    nick_name = Column(String(64), default="")
    gender = Column(String(4), default="")           # 男 / 女
    birthday = Column(Date, nullable=True)
    height = Column(Float, default=0)                 # cm
    weight = Column(Float, default=0)                 # 斤
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
