"""健康知识 Schema"""
from pydantic import BaseModel


class ArticleResponse(BaseModel):
    id: int
    title: str
    sub_title: str
    tag: str
    content: str
    is_favorited: bool = False

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    total: int
    articles: list[ArticleResponse]
