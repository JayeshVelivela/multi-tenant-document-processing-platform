"""
Document-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.document import DocumentStatus


class DocumentCreate(BaseModel):
    """Schema for document upload (metadata only, file handled separately)."""
    filename: str
    file_size: int = Field(..., gt=0, description="File size in bytes")
    mime_type: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: Optional[str]
    status: DocumentStatus
    extracted_metadata: Optional[Dict[str, Any]]
    error_message: Optional[str]
    tenant_id: int
    uploaded_by_user_id: int
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for paginated document list response."""
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentQueryParams(BaseModel):
    """Schema for document query parameters."""
    status: Optional[DocumentStatus] = None
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

