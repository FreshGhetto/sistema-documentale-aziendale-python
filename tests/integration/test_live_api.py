import os
from pathlib import Path
from uuid import uuid4

import pytest
import requests


BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")
USERNAME = os.getenv("TEST_USERNAME", "admin")
PASSWORD = os.getenv("TEST_PASSWORD", "Admin123!")
RUN_INTEGRATION_TESTS = os.getenv("RUN_INTEGRATION_TESTS", "0") == "1"
DATASET_FILE = Path(os.getenv("TEST_DATASET_FILE", "dataset/01_contratto_fornitura.txt"))


pytestmark = pytest.mark.integration


@pytest.mark.skipif(not RUN_INTEGRATION_TESTS, reason="Abilitare RUN_INTEGRATION_TESTS=1 per usare le API live.")
def test_health_endpoint_is_available() -> None:
    response = requests.get(f"{BASE_URL}/health", timeout=10)

    assert response.status_code == 200
    payload = response.json()
    assert payload["app"] == "ok"
    assert "mongo" in payload
    assert "solr" in payload


@pytest.mark.skipif(not RUN_INTEGRATION_TESTS, reason="Abilitare RUN_INTEGRATION_TESTS=1 per usare le API live.")
def test_login_returns_token_or_managed_error() -> None:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=15,
    )

    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload


@pytest.mark.skipif(not RUN_INTEGRATION_TESTS, reason="Abilitare RUN_INTEGRATION_TESTS=1 per usare le API live.")
def test_upload_search_detail_and_download_flow() -> None:
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=15,
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    tag = f"integration-{uuid4().hex[:8]}"

    with DATASET_FILE.open("rb") as handle:
        upload_response = requests.post(
            f"{BASE_URL}/documents/upload",
            headers=headers,
            files={"files": (DATASET_FILE.name, handle, "text/plain")},
            data={
                "document_type": "contratto",
                "author": "Ufficio Acquisti",
                "tags": tag,
                "use_ai": "true",
            },
            timeout=30,
        )
    assert upload_response.status_code == 200
    uploaded = upload_response.json()["uploaded"][0]
    assert uploaded["document_type"] == "contratto"
    assert uploaded["ai_category"] == "contratto"
    document_id = uploaded["id"]

    search_response = requests.get(
        f"{BASE_URL}/search",
        headers=headers,
        params={"q": "fornitura", "document_type": "contratto", "page": 1, "page_size": 10},
        timeout=20,
    )
    assert search_response.status_code == 200
    results = search_response.json()["results"]
    assert any(item["id"] == document_id for item in results)

    detail_response = requests.get(f"{BASE_URL}/documents/{document_id}", headers=headers, timeout=20)
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == document_id
    assert "fornitura" in detail["extracted_text"].lower()
    assert detail["file_url"].endswith("/download")

    download_response = requests.get(f"{BASE_URL}{detail['file_url']}", headers=headers, timeout=20)
    assert download_response.status_code == 200
    assert b"Contratto di fornitura" in download_response.content
