from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import get_settings
from app.dependencies import get_current_user
from app.schemas import AIClassificationResponse, DocumentResponse, UploadResult
from app.services import audit_service
from app.services.ai_service import classify_document
from app.services.document_service import (
    create_document_record,
    get_document_by_id,
    parse_metadata_list,
    serialize_document,
    store_file,
)


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResult)
def upload_documents(
    files: list[UploadFile] = File(...),
    metadata_json: str | None = Form(default=None),
    document_type: str | None = Form(default=None),
    author: str | None = Form(default=None),
    tags: str | None = Form(default=None),
    use_ai: bool = Form(default=False),
    current_user: dict = Depends(get_current_user),
) -> UploadResult:
    metadata_list = parse_metadata_list(metadata_json)
    shared_tags = [item.strip() for item in tags.split(",")] if tags else []

    uploaded = []
    for index, file in enumerate(files):
        file_metadata = metadata_list[index] if index < len(metadata_list) else {}
        title = file_metadata.get("title") or Path(file.filename or "").stem
        item_document_type = file_metadata.get("document_type") or document_type
        item_author = file_metadata.get("author") or author or current_user["username"]
        item_tags = file_metadata.get("tags") or shared_tags
        if not item_document_type:
            raise HTTPException(status_code=400, detail="Il campo document_type e' obbligatorio.")

        stored_filename, file_path = store_file(file)
        record = create_document_record(
            filename=file.filename or stored_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            title=title,
            document_type=item_document_type,
            author=item_author,
            tags=item_tags,
            uploaded_by=current_user["username"],
            use_ai=use_ai,
        )
        audit_service.log_action(
            current_user["username"],
            "upload_document",
            {"document_id": str(record["_id"]), "filename": record["filename"]},
        )
        uploaded.append(DocumentResponse(**serialize_document(record)))
    return UploadResult(uploaded=uploaded)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, current_user: dict = Depends(get_current_user)) -> DocumentResponse:
    record = get_document_by_id(document_id)
    audit_service.log_action(
        current_user["username"],
        "view_document",
        {"document_id": document_id},
    )
    return DocumentResponse(**serialize_document(record))


@router.get("/{document_id}/download")
def download_document(document_id: str, current_user: dict = Depends(get_current_user)) -> FileResponse:
    record = get_document_by_id(document_id)
    audit_service.log_action(
        current_user["username"],
        "download_document",
        {"document_id": document_id},
    )
    settings = get_settings()
    file_path = settings.storage_path / record["stored_filename"]
    return FileResponse(path=file_path, filename=record["filename"])


@router.post("/{document_id}/classify", response_model=AIClassificationResponse)
def classify_existing_document(document_id: str, current_user: dict = Depends(get_current_user)) -> AIClassificationResponse:
    record = get_document_by_id(document_id)
    result = classify_document(record["extracted_text"])
    audit_service.log_action(
        current_user["username"],
        "classify_document",
        {"document_id": document_id, "source": result["source"]},
    )
    return AIClassificationResponse(**result)
