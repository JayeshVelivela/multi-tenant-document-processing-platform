"""
Tenant-related Pydantic schemas.
"""
from pydantic import BaseModel
from datetime import datetime


class TenantResponse(BaseModel):
    """Schema for tenant response."""
    id: int
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

