"""
Tests for service layer.
"""
import pytest
from app.services.auth_service import AuthService
from app.services.document_service import DocumentService
from app.models.document import DocumentStatus


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = AuthService.get_password_hash(password)
    assert hashed != password
    assert AuthService.verify_password(password, hashed)
    assert not AuthService.verify_password("wrongpassword", hashed)


def test_jwt_token_creation():
    """Test JWT token creation and decoding."""
    data = {"sub": 1, "email": "test@example.com", "tenant_id": 1, "role": "user"}
    token = AuthService.create_access_token(data)
    assert token is not None
    
    decoded = AuthService.decode_token(token)
    assert decoded is not None
    assert decoded.user_id == 1
    assert decoded.email == "test@example.com"
    assert decoded.tenant_id == 1


def test_jwt_token_invalid():
    """Test JWT token decoding with invalid token."""
    decoded = AuthService.decode_token("invalid_token")
    assert decoded is None

