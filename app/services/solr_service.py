from datetime import UTC, datetime

import pysolr
from fastapi import HTTPException

from app.config import get_settings


class SolrService:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = pysolr.Solr(settings.solr_url, timeout=settings.solr_timeout_seconds, always_commit=True)

    def ping(self) -> None:
        self.client.ping()

    @staticmethod
    def _to_solr_date(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    @staticmethod
    def _escape_filter_value(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def index_document(self, record: dict) -> None:
        doc = {
            "id": str(record["_id"]),
            "title_txt_it": record["title"],
            "document_type_s": record["document_type"],
            "author_s": record["author"],
            "tags_ss": record.get("tags", []),
            "uploaded_at_dt": self._to_solr_date(record["uploaded_at"]),
            "content_txt_it": record["extracted_text"],
            "ai_category_s": record.get("ai_category"),
            "ai_summary_txt_it": record.get("ai_summary"),
        }
        self.client.add([doc])

    def search(
        self,
        *,
        query: str,
        page: int,
        page_size: int,
        document_type: str | None,
        author: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict:
        filters: list[str] = []
        if document_type:
            filters.append(f'document_type_s:"{self._escape_filter_value(document_type)}"')
        if author:
            filters.append(f'author_s:"{self._escape_filter_value(author)}"')
        if date_from or date_to:
            start = self._to_solr_date(date_from) if date_from else "*"
            end = self._to_solr_date(date_to) if date_to else "*"
            filters.append(f"uploaded_at_dt:[{start} TO {end}]")

        try:
            results = self.client.search(
                q=query or "*:*",
                fq=filters,
                start=(page - 1) * page_size,
                rows=page_size,
                **{
                    "defType": "edismax",
                    "qf": "title_txt_it^3 content_txt_it ai_summary_txt_it^2",
                    "fl": "*,score",
                    "hl": "true",
                    "hl.fl": "content_txt_it",
                    "hl.simple.pre": "<mark>",
                    "hl.simple.post": "</mark>",
                },
            )
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Solr non raggiungibile o query non valida.") from exc

        highlighting = getattr(results, "highlighting", {})
        items = []
        for doc in results.docs:
            snippet_parts = highlighting.get(doc["id"], {}).get("content_txt_it", [])
            items.append(
                {
                    "id": doc["id"],
                    "title": doc.get("title_txt_it", ""),
                    "document_type": doc.get("document_type_s", ""),
                    "author": doc.get("author_s", ""),
                    "tags": doc.get("tags_ss", []),
                    "uploaded_at": datetime.fromisoformat(doc["uploaded_at_dt"].replace("Z", "+00:00"))
                    if doc.get("uploaded_at_dt")
                    else None,
                    "score": doc.get("score"),
                    "snippet": " ... ".join(snippet_parts) if snippet_parts else None,
                }
            )
        return {"hits": results.hits, "items": items}


solr_service = SolrService()
