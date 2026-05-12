from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.config import get_settings


class MongoManager:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = MongoClient(self.settings.mongo_uri, serverSelectionTimeoutMS=3000)

    @property
    def client(self) -> MongoClient:
        return self._client

    @property
    def database(self) -> Database:
        return self.client[self.settings.mongo_db_name]

    @property
    def documents(self) -> Collection:
        return self.database["documents"]

    @property
    def users(self) -> Collection:
        return self.database["users"]

    @property
    def audit_log(self) -> Collection:
        return self.database["audit_log"]

    def ping(self) -> None:
        self.client.admin.command("ping")

    def ensure_indexes(self) -> None:
        self.documents.create_index("title")
        self.documents.create_index("document_type")
        self.documents.create_index("author")
        self.documents.create_index("uploaded_at")
        self.users.create_index("username", unique=True)
        self.audit_log.create_index("created_at")


mongo_manager = MongoManager()
