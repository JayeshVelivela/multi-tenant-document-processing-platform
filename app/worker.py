"""
Background worker for processing documents asynchronously.
"""
import os
from rq import Worker, Queue, Connection
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db_context
from app.models.document import DocumentStatus
from app.services.document_service import DocumentService
from app.services.document_processor import DocumentProcessor
from app.services.queue_service import redis_conn, document_queue


def process_document(document_id: int, tenant_id: int):
    """
    Process a document: extract real metadata from the actual file.
    """
    processor = DocumentProcessor()
    
    with get_db_context() as db:
        # Get document
        document = DocumentService.get_document_by_id(db, document_id, tenant_id)
        if not document:
            raise ValueError(f"Document {document_id} not found for tenant {tenant_id}")
        
        # Update status to processing
        DocumentService.update_document_status(
            db=db,
            document_id=document_id,
            tenant_id=tenant_id,
            status=DocumentStatus.PROCESSING
        )
        
        try:
            # Check if file exists
            if not os.path.exists(document.file_path):
                raise FileNotFoundError(f"File not found: {document.file_path}")
            
            # Process the actual document
            extracted_metadata = processor.process_document(
                file_path=document.file_path,
                filename=document.original_filename
            )
            
            # Update document with extracted metadata
            DocumentService.update_document_status(
                db=db,
                document_id=document_id,
                tenant_id=tenant_id,
                status=DocumentStatus.COMPLETED,
                extracted_metadata=extracted_metadata
            )
            
            return {
                "document_id": document_id,
                "status": "completed",
                "metadata": extracted_metadata
            }
            
        except Exception as e:
            # Update document with error
            error_msg = str(e)
            DocumentService.update_document_status(
                db=db,
                document_id=document_id,
                tenant_id=tenant_id,
                status=DocumentStatus.FAILED,
                error_message=error_msg
            )
            raise


def start_worker():
    """Start the RQ worker to process jobs."""
    with Connection(redis_conn):
        worker = Worker([document_queue])
        worker.work()


if __name__ == "__main__":
    print("Starting document processing worker...")
    start_worker()

