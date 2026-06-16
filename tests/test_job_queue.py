"""Unit tests for job queue"""

import pytest
from unittest.mock import Mock
from grogui.core.job_queue import JobQueue, Job, JobStatus


class TestJobQueue:
    """Test JobQueue functionality"""

    @pytest.fixture
    def queue(self):
        """Create JobQueue instance"""
        return JobQueue(max_workers=2)

    def test_initialization(self, queue):
        """Test queue initialization"""
        assert queue.max_workers == 2
        assert len(queue.jobs) == 0

    def test_submit_job(self, queue):
        """Test job submission"""
        job = queue.submit_job('job1', 'project1', 'command1')
        assert job.job_id == 'job1'
        assert job.status == JobStatus.PENDING
        assert 'job1' in queue.jobs

    def test_get_job(self, queue):
        """Test retrieving job"""
        queue.submit_job('job1', 'project1', 'command1')
        job = queue.get_job('job1')
        assert job is not None
        assert job.job_id == 'job1'

    def test_get_job_status(self, queue):
        """Test getting job status"""
        queue.submit_job('job1', 'project1', 'command1')
        status = queue.get_job_status('job1')
        assert status == 'pending'

    def test_cancel_job(self, queue):
        """Test job cancellation"""
        queue.submit_job('job1', 'project1', 'command1')
        cancelled = queue.cancel_job('job1')
        assert cancelled == True
        assert queue.get_job_status('job1') == 'cancelled'

    def test_queue_status(self, queue):
        """Test queue status"""
        queue.submit_job('job1', 'project1', 'command1')
        queue.submit_job('job2', 'project2', 'command2')
        status = queue.get_queue_status()
        assert status['total_jobs'] == 2
        assert status['active_workers'] == 0
        assert status['max_workers'] == 2

    def test_job_dataclass(self):
        """Test Job dataclass"""
        job = Job(
            job_id='test_job',
            project_name='test_project',
            command='gmx mdrun'
        )
        assert job.job_id == 'test_job'
        assert job.status == JobStatus.PENDING
        job_dict = job.to_dict()
        assert 'job_id' in job_dict
        assert job_dict['status'] == 'pending'
