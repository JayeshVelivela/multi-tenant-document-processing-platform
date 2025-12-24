"""
Tenant service for tenant management and isolation enforcement.
"""
from sqlalchemy.orm import Session
from typing import Optional

from app.models.tenant import Tenant


class TenantService:
    """Service for tenant operations."""
    
    @staticmethod
    def get_tenant_by_id(db: Session, tenant_id: int) -> Optional[Tenant]:
        """Get tenant by ID."""
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    @staticmethod
    def get_tenant_by_slug(db: Session, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        return db.query(Tenant).filter(Tenant.slug == slug).first()
    
    @staticmethod
    def enforce_tenant_isolation(query, tenant_id: int):
        """
        Enforce tenant isolation by filtering queries by tenant_id.
        This is a critical security function to prevent data leakage.
        """
        return query.filter_by(tenant_id=tenant_id)

