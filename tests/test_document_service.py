import pytest
from fastapi import HTTPException

from app.services.document_service import parse_metadata_list


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
