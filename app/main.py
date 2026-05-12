from contextlib import suppress

from fastapi import FastAPI

from app.config import get_settings
from app.database import mongo_manager
from app.routers import auth, documents, search
from app.security import hash_password
from app.services.solr_service import solr_service


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Backend per la gestione documentale con MongoDB, Solr e supporto AI.",
        version="1.0.0",
    )

    @app.on_event("startup")
    def startup() -> None:
        with suppress(Exception):
            mongo_manager.ping()
            mongo_manager.ensure_indexes()
            if not mongo_manager.users.find_one({"username": settings.default_admin_username}):
                mongo_manager.users.insert_one(
                    {
                        "username": settings.default_admin_username,
                        "password_hash": hash_password(settings.default_admin_password),
                        "role": "admin",
                    }
                )
        with suppress(Exception):
            solr_service.ping()

    @app.get("/health")
    def health() -> dict:
        mongo_status = "ok"
        solr_status = "ok"
        try:
            mongo_manager.ping()
        except Exception:
            mongo_status = "error"
        try:
            solr_service.ping()
        except Exception:
            solr_status = "error"
        return {"app": "ok", "mongo": mongo_status, "solr": solr_status}

    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(search.router)
    return app


app = create_app()
