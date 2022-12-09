from datetime import date, datetime
from pydantic import BaseModel, EmailStr, SecretStr


class Publication(BaseModel):
    name: dict[str, str] | None = None
    # code == 'computer CV' , code == 'NLP'
    code: str
    description: dict[str, str] | None = None
    publisher: str | None = None
    publication_languages: list[str] | None = None
    publication_category: str | None = None
    publication_cycle: str | None = None
    issn: str | None = None
    isbn: str | None = None
    funding_date: date | None = None
    editor_in_chief: str | None = None
    editors: dict[str, str] | None = None


class Issue(BaseModel):
    publication_id: int
    code: str
    cover_image: str
    cover_image_author: str | None = None
    issue_number: str
    issue_language: str | None = None
    issue_title: str | None = None
    issue_description: str | None = None
    # login required
    issue_pdf: str | None = None


class Collection(BaseModel):
    name: str
    description: str | None = None


class Post(BaseModel):
    title: str
    language: str
    collections: list[Collection] | None = None
    description: str | None = None
    author: str | None = None
    published_datetime: datetime | None = None
    updated_datetime: datetime | None = None
    content: str | None = None


class Page(BaseModel):
    title: str
    description: str | None = None
    language: str
    author: str | None = None
    published_datetime: datetime | None = None
    updated_datetime: datetime | None = None
    content: str | None = None


class User(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr
    created_at: datetime | None = None
    updated_at: datetime | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_superuser: bool = False  # can edit user permissions, can do everything
    is_staff: bool = False  # can upload new issue, publish new post (also update and delete)
    is_verified: bool = False  # email verified
