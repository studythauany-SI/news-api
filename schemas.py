from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NewsBase(BaseModel):
    title: str
    content: str


class NewsCreate(NewsBase):
    pass


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class News(NewsBase):
    id: str
    author_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
