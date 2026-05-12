import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from bson import ObjectId
from docx import Document as DocxDocument
from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

from app.config import get_settings
from app.database import mongo_manager
from app.services.ai_service import classify_document
from app.services.solr_service import solr_service


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def parse_metadata_list(metadata_json: str | None) -> list[dict]:
    if not metadata_json:
        return []
    try:
        parsed = json.loads(metadata_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Il campo metadata_json non contiene JSON valido.") from exc
    if not isinstance(parsed, list):
        raise HTTPException(status_code=400, detail="metadata_json deve essere una lista di oggetti.")
    return parsed


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        return file_path.read_text(encoding="utf-8")
    if suffix == ".docx":
        document = DocxDocument(file_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text).strip()
    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    raise HTTPException(status_code=400, detail=f"Formato non supportato: {suffix}")


def store_file(upload_file: UploadFile) -> tuple[str, Path]:
    settings = get_settings()
    suffix = Path(upload_file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato non supportato per {upload_file.filename}. Ammessi: PDF, DOCX, TXT.",
        )
    stored_name = f"{uuid4().hex}{suffix}"
    destination = settings.storage_path / stored_name
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return stored_name, destination


def create_document_record(
    *,
    filename: str,
    stored_filename: str,
    file_path: Path,
    title: str,
    document_type: str,
    author: str,
    tags: list[str],
    uploaded_by: str,
    use_ai: bool,
) -> dict:
    extracted_text = extract_text(file_path)
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail=f"Il file {filename} non contiene testo estraibile.")

    ai_data = {"category": None, "summary": None}
    if use_ai:
        ai_data = classify_document(extracted_text)

    record = {
        "filename": filename,
        "stored_filename": stored_filename,
        "title": title,
        "document_type": document_type,
        "author": author,
        "tags": tags,
        "uploaded_at": datetime.now(UTC),
        "uploaded_by": uploaded_by,
        "extracted_text": extracted_text,
        "ai_category": ai_data.get("category"),
        "ai_summary": ai_data.get("summary"),
    }
    result = mongo_manager.documents.insert_one(record)
    record["_id"] = result.inserted_id
    solr_service.index_document(record)
    return record


def serialize_document(record: dict) -> dict:
    return {
        "id": str(record["_id"]),
        "filename": record["filename"],
        "title": record["title"],
        "document_type": record["document_type"],
        "author": record["author"],
        "tags": record.get("tags", []),
        "uploaded_at": record["uploaded_at"],
        "uploaded_by": record["uploaded_by"],
        "extracted_text": record["extracted_text"],
        "ai_category": record.get("ai_category"),
        "ai_summary": record.get("ai_summary"),
        "file_url": f"/documents/{record['_id']}/download",
    }


def get_document_by_id(document_id: str) -> dict:
    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=400, detail="ID documento non valido.")
    record = mongo_manager.documents.find_one({"_id": ObjectId(document_id)})
    if not record:
        raise HTTPException(status_code=404, detail="Documento non trovato.")
    return record
