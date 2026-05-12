from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user
from app.schemas import SearchResponse, SearchResultItem
from app.services import audit_service
from app.services.solr_service import solr_service


router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search_documents(
    q: str = Query(default="*:*"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    document_type: str | None = Query(default=None),
    author: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
) -> SearchResponse:
    search_result = solr_service.search(
        query=q,
        page=page,
        page_size=page_size,
        document_type=document_type,
        author=author,
        date_from=date_from,
        date_to=date_to,
    )
    audit_service.log_action(
        current_user["username"],
        "search_documents",
        {
            "query": q,
            "page": page,
            "page_size": page_size,
            "document_type": document_type,
            "author": author,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
        },
    )
    return SearchResponse(
        total=search_result["hits"],
        page=page,
        page_size=page_size,
        results=[SearchResultItem(**item) for item in search_result["items"]],
    )
