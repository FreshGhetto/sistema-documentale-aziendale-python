from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    role: str


class UploadMetadata(BaseModel):
    title: str | None = None
    document_type: str = Field(..., description="es. contratto, fattura, cv")
    author: str
    tags: list[str] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    id: str
    filename: str
    title: str
    document_type: str
    author: str
    tags: list[str]
    uploaded_at: datetime
    uploaded_by: str
    extracted_text: str
    ai_category: str | None = None
    ai_summary: str | None = None
    file_url: str


class UploadResult(BaseModel):
    uploaded: list[DocumentResponse]


class SearchResultItem(BaseModel):
    id: str
    title: str
    document_type: str
    author: str
    tags: list[str]
    uploaded_at: datetime | None = None
    score: float | None = None
    snippet: str | None = None


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[SearchResultItem]


class AIClassificationResponse(BaseModel):
    category: str
    summary: str
    source: str
