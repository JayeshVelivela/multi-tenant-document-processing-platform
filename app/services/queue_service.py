"""
Redis queue service for background job management.
"""
import redis
from rq import Queue
from typing import Dict, Any

from app.config import settings

# Redis connection
redis_conn = redis.from_url(settings.redis_url)

# RQ Queue
document_queue = Queue(settings.redis_queue_name, connection=redis_conn)


class QueueService:
    """Service for managing background job queues."""
    
    @staticmethod
    def enqueue_document_processing(document_id: int, tenant_id: int) -> str:
        """
        Enqueue a document processing job.
        Returns job ID.
        """
        from app.worker import process_document
        
        job = document_queue.enqueue(
            process_document,
            document_id,
            tenant_id,
            job_timeout='10m',  # 10 minute timeout
            job_id=f"doc_{document_id}_{tenant_id}"
        )
        
        return job.id
    
    @staticmethod
    def get_job_status(job_id: str) -> Dict[str, Any]:
        """Get status of a job."""
        job = document_queue.fetch_job(job_id)
        if not job:
            return {"status": "not_found"}
        
        return {
            "status": job.get_status(),
            "result": job.result,
            "error": str(job.exc_info) if job.exc_info else None
        }

