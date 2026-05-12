import json
import os
from pathlib import Path

import requests


BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8002")
USERNAME = os.getenv("TEST_USERNAME", "admin")
PASSWORD = os.getenv("TEST_PASSWORD", "Admin123!")
DATASET_FILE = Path(os.getenv("TEST_DATASET_FILE", "dataset/01_contratto_fornitura.txt"))
DOCUMENT_TYPE = os.getenv("TEST_DOCUMENT_TYPE", "contratto")
AUTHOR = os.getenv("TEST_AUTHOR", "Ufficio Acquisti")
TAGS = os.getenv("TEST_TAGS", "demo,smoke")


def print_step(title: str, payload: object) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


def main() -> int:
    health_response = requests.get(f"{BASE_URL}/health", timeout=10)
    print_step("health", {"status_code": health_response.status_code, "body": health_response.json()})

    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=15,
    )
    login_body = login_response.json()
    print_step("login", {"status_code": login_response.status_code, "body": login_body})
    if login_response.status_code != 200:
        return 1

    token = login_body["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with DATASET_FILE.open("rb") as handle:
        files = {"files": (DATASET_FILE.name, handle, "text/plain")}
        form = {
            "document_type": DOCUMENT_TYPE,
            "author": AUTHOR,
            "tags": TAGS,
            "use_ai": "true",
        }
        upload_response = requests.post(
            f"{BASE_URL}/documents/upload",
            headers=headers,
            files=files,
            data=form,
            timeout=30,
        )
    upload_body = upload_response.json()
    print_step("upload", {"status_code": upload_response.status_code, "body": upload_body})
    if upload_response.status_code != 200:
        return 1

    document_id = upload_body["uploaded"][0]["id"]
    search_response = requests.get(
        f"{BASE_URL}/search",
        headers=headers,
        params={"q": "fornitura", "document_type": DOCUMENT_TYPE, "page": 1, "page_size": 10},
        timeout=20,
    )
    print_step("search", {"status_code": search_response.status_code, "body": search_response.json()})

    detail_response = requests.get(f"{BASE_URL}/documents/{document_id}", headers=headers, timeout=20)
    print_step("detail", {"status_code": detail_response.status_code, "body": detail_response.json()})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
