"""
Document API routes.
"""
import os
import json
import csv
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Request
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.models.document import DocumentStatus
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.services.document_service import DocumentService
from app.services.queue_service import QueueService
from app.config import settings
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing.
    Returns immediately after enqueueing the processing job.
    """
    # Create document record
    document = DocumentService.create_document(
        db=db,
        file=file,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )
    
    # Enqueue processing job
    try:
        QueueService.enqueue_document_processing(document.id, current_user.tenant_id)
    except Exception as e:
        # If queue fails, mark document as failed
        DocumentService.update_document_status(
            db=db,
            document_id=document.id,
            tenant_id=current_user.tenant_id,
            status=DocumentStatus.FAILED,
            error_message=f"Failed to enqueue processing: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enqueue document for processing"
        )
    
    return document


@router.get("/", response_model=DocumentListResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
def list_documents(
    request: Request,
    status: DocumentStatus | None = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List documents for the current user's tenant with pagination.
    """
    documents, total = DocumentService.list_documents(
        db=db,
        tenant_id=current_user.tenant_id,
        status_filter=status,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return DocumentListResponse(
        items=documents,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{document_id}", response_model=DocumentResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
def get_document(
    request: Request,
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID (tenant-isolated).
    """
    document = DocumentService.get_document_by_id(
        db=db,
        document_id=document_id,
        tenant_id=current_user.tenant_id
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.get("/{document_id}/download")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
def download_document(
    request: Request,
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Download the original document file (tenant-isolated).
    """
    document = DocumentService.get_document_by_id(
        db=db,
        document_id=document_id,
        tenant_id=current_user.tenant_id
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on server"
        )
    
    return FileResponse(
        path=document.file_path,
        filename=document.original_filename,
        media_type=document.mime_type or "application/octet-stream"
    )


@router.get("/export/json")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
def export_documents_json(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export all documents with metadata as JSON (tenant-isolated).
    Only exports documents belonging to the current user's tenant.
    """
    # Explicitly enforce tenant isolation
    documents, _ = DocumentService.list_documents(
        db=db,
        tenant_id=current_user.tenant_id,  # CRITICAL: Only current user's tenant
        status_filter=None,
        page=1,
        page_size=10000  # Get all documents
    )
    
    # Convert to dict format
    export_data = []
    for doc in documents:
        doc_dict = {
            "id": doc.id,
            "filename": doc.original_filename,
            "status": doc.status.value if hasattr(doc.status, 'value') else str(doc.status),
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "processed_at": doc.processed_at.isoformat() if doc.processed_at else None,
            "extracted_metadata": doc.extracted_metadata if isinstance(doc.extracted_metadata, dict) else json.loads(doc.extracted_metadata) if doc.extracted_metadata else None
        }
        export_data.append(doc_dict)
    
    return Response(
        content=json.dumps(export_data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=documents_export.json"}
    )


@router.get("/export/csv")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
def export_documents_csv(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export all documents with metadata as CSV (tenant-isolated).
    Only exports documents belonging to the current user's tenant.
    """
    # Explicitly enforce tenant isolation
    documents, _ = DocumentService.list_documents(
        db=db,
        tenant_id=current_user.tenant_id,  # CRITICAL: Only current user's tenant
        status_filter=None,
        page=1,
        page_size=10000  # Get all documents
    )
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ID", "Filename", "Status", "File Size (bytes)", "MIME Type",
        "Document Type", "Pages", "Words", "Language",
        "Dates", "Amounts", "Companies", "Text Preview",
        "Created At", "Processed At"
    ])
    
    # Write data
    for doc in documents:
        metadata = doc.extracted_metadata if isinstance(doc.extracted_metadata, dict) else json.loads(doc.extracted_metadata) if doc.extracted_metadata else {}
        
        writer.writerow([
            doc.id,
            doc.original_filename,
            doc.status.value if hasattr(doc.status, 'value') else str(doc.status),
            doc.file_size,
            doc.mime_type or "",
            metadata.get("document_type", ""),
            metadata.get("page_count", ""),
            metadata.get("word_count", ""),
            metadata.get("language", ""),
            ", ".join(metadata.get("entities", {}).get("dates", [])) if metadata.get("entities") else "",
            ", ".join(metadata.get("entities", {}).get("amounts", [])) if metadata.get("entities") else "",
            ", ".join(metadata.get("entities", {}).get("companies", [])) if metadata.get("entities") else "",
            (metadata.get("extracted_text_preview", "") or "")[:200],
            doc.created_at.isoformat() if doc.created_at else "",
            doc.processed_at.isoformat() if doc.processed_at else ""
        ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=documents_export.csv"}
    )

