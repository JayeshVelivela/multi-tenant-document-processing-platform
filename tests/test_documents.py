"""
Tests for document endpoints.
"""
import pytest
from fastapi import status
from io import BytesIO


def test_upload_document(client, auth_token, db_session, test_user):
    """Test document upload."""
    file_content = b"Test document content"
    file = ("test.pdf", BytesIO(file_content), "application/pdf")
    
    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": file}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["original_filename"] == "test.pdf"
    assert data["status"] == "pending"
    assert data["tenant_id"] == test_user.tenant_id


def test_upload_document_no_auth(client):
    """Test document upload without authentication."""
    file_content = b"Test document content"
    file = ("test.pdf", BytesIO(file_content), "application/pdf")
    
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": file}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_documents(client, auth_token, db_session, test_user):
    """Test listing documents."""
    response = client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


def test_list_documents_with_status_filter(client, auth_token):
    """Test listing documents with status filter."""
    response = client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {auth_token}"},
        params={"status": "pending"}
    )
    assert response.status_code == status.HTTP_200_OK


def test_get_document_not_found(client, auth_token):
    """Test getting non-existent document."""
    response = client.get(
        "/api/v1/documents/99999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

