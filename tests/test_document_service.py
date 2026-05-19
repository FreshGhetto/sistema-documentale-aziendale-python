from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from bson import ObjectId
from fastapi import HTTPException

from app.services.document_service import normalize_tags, parse_metadata_list, update_document_ai_classification


def test_parse_metadata_list_accepts_valid_json_list() -> None:
    payload = '[{"title":"Doc 1","document_type":"contratto","author":"Mario","tags":["a","b"]}]'

    result = parse_metadata_list(payload)

    assert isinstance(result, list)
    assert result[0]["title"] == "Doc 1"


def test_parse_metadata_list_rejects_invalid_json() -> None:
    with pytest.raises(HTTPException) as exc_info:
        parse_metadata_list("{invalid}")

    assert exc_info.value.status_code == 400


def test_parse_metadata_list_rejects_non_list_json() -> None:
    with pytest.raises(HTTPException) as exc_info:
        parse_metadata_list('{"title":"Doc 1"}')

    assert exc_info.value.status_code == 400


def test_parse_metadata_list_rejects_non_object_items() -> None:
    with pytest.raises(HTTPException) as exc_info:
        parse_metadata_list('["bad"]')

    assert exc_info.value.status_code == 400


def test_normalize_tags_accepts_comma_separated_string() -> None:
    assert normalize_tags("fornitori, 2026, , urgente ") == ["fornitori", "2026", "urgente"]


def test_normalize_tags_accepts_list_of_strings() -> None:
    assert normalize_tags([" fornitori ", "", "2026"]) == ["fornitori", "2026"]


def test_normalize_tags_rejects_invalid_items() -> None:
    with pytest.raises(HTTPException) as exc_info:
        normalize_tags(["ok", 12])

    assert exc_info.value.status_code == 400


def test_update_document_ai_classification_persists_and_indexes(monkeypatch) -> None:
    updates = []
    indexed_records = []
    record = {
        "_id": ObjectId(),
        "filename": "doc.txt",
        "stored_filename": "stored.txt",
        "title": "Doc",
        "document_type": "altro",
        "author": "Mario",
        "tags": [],
        "uploaded_at": datetime.now(UTC),
        "uploaded_by": "admin",
        "extracted_text": "Fattura con IVA",
        "ai_category": None,
        "ai_summary": None,
    }

    class FakeDocuments:
        @staticmethod
        def update_one(selector: dict, update: dict) -> None:
            updates.append((selector, update))

    monkeypatch.setattr(
        "app.services.document_service.classify_document",
        lambda _: {"category": "fattura", "summary": "Sintesi", "source": "fallback"},
    )
    monkeypatch.setattr("app.services.document_service.mongo_manager", SimpleNamespace(documents=FakeDocuments()))
    monkeypatch.setattr("app.services.document_service.solr_service.index_document", lambda item: indexed_records.append(item.copy()))

    result = update_document_ai_classification(record)

    assert result["category"] == "fattura"
    assert record["ai_category"] == "fattura"
    assert updates[0][1]["$set"]["ai_summary"] == "Sintesi"
    assert indexed_records[0]["ai_category"] == "fattura"
