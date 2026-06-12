"""健康知识模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, func
from app.database import Base


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    sub_title = Column(String(256), default="")
    tag = Column(String(16), default="")
    content = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class KnowledgeFavorite(Base):
    __tablename__ = "knowledge_favorites"
    __table_args__ = (UniqueConstraint("user_id", "article_id", name="uq_fav_user_article"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("knowledge_articles.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
