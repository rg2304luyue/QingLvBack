"""健康知识路由：文章列表 + 收藏"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.knowledge import KnowledgeArticle, KnowledgeFavorite
from app.schemas.knowledge import ArticleResponse, ArticleListResponse

router = APIRouter(prefix="/api/knowledge", tags=["健康知识"])


@router.get("/articles", response_model=ArticleListResponse)
def list_articles(
    tag: str | None = Query(None, description="按标签筛选：饮食/运动/睡眠/心理"),
    keyword: str | None = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取文章列表（带收藏状态）"""
    q = db.query(KnowledgeArticle)
    if tag:
        q = q.filter(KnowledgeArticle.tag == tag)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            (KnowledgeArticle.title.like(like)) |
            (KnowledgeArticle.sub_title.like(like)) |
            (KnowledgeArticle.content.like(like))
        )
    articles = q.order_by(KnowledgeArticle.sort_order.asc()).all()

    # 获取当前用户的收藏 article_id 集合
    fav_ids = set(
        r[0] for r in db.query(KnowledgeFavorite.article_id)
        .filter(KnowledgeFavorite.user_id == current_user.id)
        .all()
    )

    result = []
    for a in articles:
        result.append(ArticleResponse(
            id=a.id, title=a.title, sub_title=a.sub_title,
            tag=a.tag, content=a.content,
            is_favorited=a.id in fav_ids,
        ))
    return ArticleListResponse(total=len(result), articles=result)


@router.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取单篇文章详情"""
    article = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    is_fav = db.query(KnowledgeFavorite).filter(
        KnowledgeFavorite.user_id == current_user.id,
        KnowledgeFavorite.article_id == article_id,
    ).first() is not None
    return ArticleResponse(
        id=article.id, title=article.title, sub_title=article.sub_title,
        tag=article.tag, content=article.content, is_favorited=is_fav,
    )


@router.post("/favorites/{article_id}")
def add_favorite(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """收藏文章"""
    article = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    existing = db.query(KnowledgeFavorite).filter(
        KnowledgeFavorite.user_id == current_user.id,
        KnowledgeFavorite.article_id == article_id,
    ).first()
    if not existing:
        fav = KnowledgeFavorite(user_id=current_user.id, article_id=article_id)
        db.add(fav)
        db.commit()
    return {"message": "已收藏"}


@router.delete("/favorites/{article_id}")
def remove_favorite(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """取消收藏"""
    db.query(KnowledgeFavorite).filter(
        KnowledgeFavorite.user_id == current_user.id,
        KnowledgeFavorite.article_id == article_id,
    ).delete()
    db.commit()
    return {"message": "已取消收藏"}


@router.get("/favorites", response_model=ArticleListResponse)
def list_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取收藏的文章列表"""
    fav_article_ids = [
        r[0] for r in db.query(KnowledgeFavorite.article_id)
        .filter(KnowledgeFavorite.user_id == current_user.id)
        .all()
    ]
    if not fav_article_ids:
        return ArticleListResponse(total=0, articles=[])

    articles = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.id.in_(fav_article_ids)
    ).order_by(KnowledgeArticle.sort_order.asc()).all()

    result = [
        ArticleResponse(
            id=a.id, title=a.title, sub_title=a.sub_title,
            tag=a.tag, content=a.content, is_favorited=True,
        )
        for a in articles
    ]
    return ArticleListResponse(total=len(result), articles=result)
