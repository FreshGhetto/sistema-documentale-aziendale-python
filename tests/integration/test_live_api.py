import os

import pytest
import requests


BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8002")
USERNAME = os.getenv("TEST_USERNAME", "admin")
PASSWORD = os.getenv("TEST_PASSWORD", "Admin123!")
RUN_INTEGRATION_TESTS = os.getenv("RUN_INTEGRATION_TESTS", "0") == "1"


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

    assert response.status_code in {200, 401, 503}
    payload = response.json()
    if response.status_code == 200:
        assert "access_token" in payload
    else:
        assert "detail" in payload
