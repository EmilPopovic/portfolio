from pydantic import BaseModel
from datetime import date

class Author(BaseModel):
    name: str

class Post(BaseModel):
    slug: str
    file: str
    title: str
    authors: list[Author]
    created: date
    updated: date
    description: str
    tags: list[str]
    draft: bool
    featured: bool
    cover_image: str
    attachments: list[str]

class Series(BaseModel):
    slug: str
    title: str
    description: str
    authors: list[Author]
    created: date
    status: str
    cover_image: str
    posts: list[Post]
