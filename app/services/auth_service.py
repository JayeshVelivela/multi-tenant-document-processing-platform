"""
Authentication service for user registration, login, and JWT token management.
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.schemas.auth import UserCreate, TokenData


class AuthService:
    """Service for authentication and authorization."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            # Decode the hashed password if it's a string
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            if isinstance(plain_password, str):
                plain_password = plain_password.encode('utf-8')
            return bcrypt.checkpw(plain_password, hashed_password)
        except Exception:
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        # Generate salt and hash password
        if isinstance(password, str):
            password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        # Ensure all values are JSON serializable
        to_encode = {k: v for k, v in to_encode.items() if v is not None}
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        # jwt.encode returns bytes in some versions, convert to string
        if isinstance(encoded_jwt, bytes):
            encoded_jwt = encoded_jwt.decode('utf-8')
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token."""
        if not token:
            return None
            
        # Remove any whitespace
        token = token.strip()
        
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm],
                options={"verify_signature": True, "verify_exp": True}
            )
            # sub is stored as string in JWT, convert back to int
            user_id_str = payload.get("sub")
            email = payload.get("email")
            tenant_id = payload.get("tenant_id")
            role = payload.get("role")
            
            if user_id_str is None:
                return None
            
            # Convert string back to int
            user_id = int(user_id_str)
            
            return TokenData(
                user_id=user_id,
                email=email,
                tenant_id=int(tenant_id) if tenant_id else None,
                role=UserRole(role) if role else None
            )
        except JWTError as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger("document_platform")
            logger.error(f"JWT decode error: {e}, token preview: {token[:20]}...")
            return None
        except Exception as e:
            # Log any other errors
            import logging
            logger = logging.getLogger("document_platform")
            logger.error(f"Token decode error: {e}, token preview: {token[:20]}...")
            return None
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Register a new user and create a UNIQUE tenant for each user.
        This ensures complete data isolation between accounts.
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create a UNIQUE tenant for each user to ensure complete isolation
        # Generate unique tenant name and slug
        # Format: "tenant_name-{unique_id}" to ensure uniqueness
        unique_id = str(uuid.uuid4())[:8]
        tenant_name = f"{user_data.tenant_name} ({user_data.email.split('@')[0]})"
        tenant_slug = f"{user_data.tenant_name.lower().replace(' ', '-')}-{unique_id}"
        
        # Ensure slug is unique (in case of collision)
        existing_tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
        if existing_tenant:
            # If collision, add more uniqueness
            tenant_slug = f"{tenant_slug}-{uuid.uuid4().hex[:4]}"
        
        # Create new tenant (always create new one for isolation)
        tenant = Tenant(
            name=tenant_name,
            slug=tenant_slug,
            is_active=True
        )
        db.add(tenant)
        db.flush()  # Get tenant ID without committing
        
        # Create user
        hashed_password = AuthService.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=UserRole.USER,
            is_active=True,
            tenant_id=tenant.id
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """Get current user from JWT token."""
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not provided",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = AuthService.decode_token(token)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive"
            )
        
        return user

