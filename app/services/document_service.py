"""
Document service for document management and processing.
"""
import os
import uuid
from pathlib import Path
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import UploadFile, HTTPException, status

from app.config import settings
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.services.tenant_service import TenantService


class DocumentService:
    """Service for document operations."""
    
    @staticmethod
    def save_uploaded_file(file: UploadFile, tenant_id: int, user_id: int) -> Tuple[str, str]:
        """
        Save uploaded file to storage and return file path and filename.
        Returns: (file_path, stored_filename)
        """
        # Create tenant-specific directory
        storage_path = Path(settings.storage_path)
        tenant_dir = storage_path / f"tenant_{tenant_id}"
        tenant_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        stored_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = tenant_dir / stored_filename
        
        # Save file
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        return str(file_path), stored_filename
    
    @staticmethod
    def create_document(
        db: Session,
        file: UploadFile,
        tenant_id: int,
        user_id: int
    ) -> Document:
        """
        Create a document record and save the file.
        """
        # Save file
        file_path, stored_filename = DocumentService.save_uploaded_file(file, tenant_id, user_id)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create document record
        document = Document(
            filename=stored_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type,
            status=DocumentStatus.PENDING,
            tenant_id=tenant_id,
            uploaded_by_user_id=user_id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
    
    @staticmethod
    def get_document_by_id(db: Session, document_id: int, tenant_id: int) -> Optional[Document]:
        """
        Get document by ID with STRICT tenant isolation enforcement.
        This ensures users can ONLY access documents from their own tenant.
        """
        # CRITICAL: Always filter by tenant_id to prevent cross-tenant data access
        document = db.query(Document).filter(
            and_(
                Document.id == document_id,
                Document.tenant_id == tenant_id  # Tenant isolation - REQUIRED
            )
        ).first()
        
        # Additional security check: verify tenant_id matches
        if document and document.tenant_id != tenant_id:
            return None
        
        return document
    
    @staticmethod
    def list_documents(
        db: Session,
        tenant_id: int,
        status_filter: Optional[DocumentStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Document], int]:
        """
        List documents for a tenant with pagination and optional status filter.
        STRICT tenant isolation - users can ONLY see documents from their tenant.
        Returns: (documents, total_count)
        """
        # CRITICAL: Base query with STRICT tenant isolation
        # This filter MUST always be applied to prevent data leakage
        query = db.query(Document).filter(Document.tenant_id == tenant_id)
        
        # Apply status filter if provided
        if status_filter:
            query = query.filter(Document.status == status_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        documents = query.order_by(Document.created_at.desc()).offset(offset).limit(page_size).all()
        
        return documents, total
    
    @staticmethod
    def update_document_status(
        db: Session,
        document_id: int,
        tenant_id: int,
        status: DocumentStatus,
        extracted_metadata: Optional[dict] = None,
        error_message: Optional[str] = None
    ) -> Optional[Document]:
        """
        Update document processing status.
        """
        document = DocumentService.get_document_by_id(db, document_id, tenant_id)
        if not document:
            return None
        
        document.status = status
        if extracted_metadata is not None:
            document.extracted_metadata = extracted_metadata
        if error_message is not None:
            document.error_message = error_message
        
        if status == DocumentStatus.COMPLETED:
            from datetime import datetime
            document.processed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(document)
        
        return document

