"""
Seed script to populate database with sample data.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import get_db_context
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.services.auth_service import AuthService


def seed_data():
    """Seed database with sample tenants and users."""
    with get_db_context() as db:
        # Create sample tenants
        tenants_data = [
            {"name": "Acme Corporation", "slug": "acme-corporation"},
            {"name": "TechStart Inc", "slug": "techstart-inc"},
            {"name": "Global Industries", "slug": "global-industries"},
        ]
        
        tenants = []
        for tenant_data in tenants_data:
            tenant = db.query(Tenant).filter(Tenant.slug == tenant_data["slug"]).first()
            if not tenant:
                tenant = Tenant(**tenant_data, is_active=True)
                db.add(tenant)
                db.flush()
            tenants.append(tenant)
        
        # Create sample users for each tenant
        users_data = [
            {
                "email": "admin@acme.com",
                "password": "admin123",
                "full_name": "Acme Admin",
                "role": UserRole.ADMIN,
                "tenant": tenants[0]
            },
            {
                "email": "user@acme.com",
                "password": "user123",
                "full_name": "Acme User",
                "role": UserRole.USER,
                "tenant": tenants[0]
            },
            {
                "email": "admin@techstart.com",
                "password": "admin123",
                "full_name": "TechStart Admin",
                "role": UserRole.ADMIN,
                "tenant": tenants[1]
            },
            {
                "email": "user@techstart.com",
                "password": "user123",
                "full_name": "TechStart User",
                "role": UserRole.USER,
                "tenant": tenants[1]
            },
            {
                "email": "admin@global.com",
                "password": "admin123",
                "full_name": "Global Admin",
                "role": UserRole.ADMIN,
                "tenant": tenants[2]
            },
        ]
        
        for user_data in users_data:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(
                    email=user_data["email"],
                    hashed_password=AuthService.get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    is_active=True,
                    tenant_id=user_data["tenant"].id
                )
                db.add(user)
        
        db.commit()
        print("✓ Seeded database with sample tenants and users")
        print("\nSample users:")
        print("  Acme Corporation:")
        print("    - admin@acme.com / admin123 (Admin)")
        print("    - user@acme.com / user123 (User)")
        print("  TechStart Inc:")
        print("    - admin@techstart.com / admin123 (Admin)")
        print("    - user@techstart.com / user123 (User)")
        print("  Global Industries:")
        print("    - admin@global.com / admin123 (Admin)")


if __name__ == "__main__":
    seed_data()

