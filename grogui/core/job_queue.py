"""Job queue management for parallel simulations"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum
import threading
import queue
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Simulation job"""
    job_id: str
    project_name: str
    command: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "project_name": self.project_name,
            "command": self.command,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
        }


class JobQueue:
    """Job queue for managing multiple simulations"""

    def __init__(self, max_workers: int = 4):
        """
        Initialize job queue.
        
        Args:
            max_workers: Maximum number of parallel jobs
        """
        self.max_workers = max_workers
        self.queue: queue.Queue = queue.Queue()
        self.jobs: Dict[str, Job] = {}
        self.running_jobs: Dict[str, threading.Thread] = {}
        self._stop_event = threading.Event()
        self.logger = logger

    def submit_job(
        self,
        job_id: str,
        project_name: str,
        command: str
    ) -> Job:
        """Submit a new job to the queue"""
        job = Job(job_id=job_id, project_name=project_name, command=command)
        self.jobs[job_id] = job
        self.queue.put(job)
        self.logger.info(f"Job submitted: {job_id}")
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)

    def get_job_status(self, job_id: str) -> Optional[str]:
        """Get job status"""
        job = self.get_job(job_id)
        return job.status.value if job else None

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if job.status == JobStatus.PENDING:
                job.status = JobStatus.CANCELLED
                self.logger.info(f"Job cancelled: {job_id}")
                return True
        return False

    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        statuses = {}
        for status_enum in JobStatus:
            statuses[status_enum.value] = sum(
                1 for job in self.jobs.values()
                if job.status == status_enum
            )
        
        return {
            "total_jobs": len(self.jobs),
            "active_workers": len(self.running_jobs),
            "max_workers": self.max_workers,
            "status_counts": statuses,
            "queue_size": self.queue.qsize(),
        }

    def start_workers(self) -> None:
        """Start worker threads"""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker,
                daemon=True,
                name=f"Worker-{i}"
            )
            worker.start()
        self.logger.info(f"Started {self.max_workers} workers")

    def _worker(self) -> None:
        """Worker thread function"""
        while not self._stop_event.is_set():
            try:
                job = self.queue.get(timeout=1)
                if job is None:  # Shutdown signal
                    break
                
                self._execute_job(job)
                self.queue.task_done()
            
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker error: {e}")

    def _execute_job(self, job: Job) -> None:
        """Execute a single job"""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        self.logger.info(f"Executing job: {job.job_id}")
        
        try:
            # Execute command (placeholder)
            # In real implementation, this would run the actual simulation
            job.result = {"output": "Job execution placeholder"}
            job.status = JobStatus.COMPLETED
            self.logger.info(f"Job completed: {job.job_id}")
        
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            self.logger.error(f"Job failed: {job.job_id} - {e}")
        
        finally:
            job.completed_at = datetime.now()

    def stop(self) -> None:
        """Stop all workers"""
        self._stop_event.set()
        self.logger.info("Job queue stopped")

    def wait_completion(self) -> None:
        """Wait for all jobs to complete"""
        self.queue.join()
        self.logger.info("All jobs completed")
