from datetime import UTC, datetime
from typing import Any

from app.database import mongo_manager


def log_action(username: str, action: str, payload: dict[str, Any]) -> None:
    mongo_manager.audit_log.insert_one(
        {
            "username": username,
            "action": action,
            "payload": payload,
            "created_at": datetime.now(UTC),
        }
    )
