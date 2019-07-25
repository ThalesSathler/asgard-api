from typing import Optional, List

from asgard.backends.jobs import ScheduledJobsBackend
from asgard.models.account import Account
from asgard.models.job import ScheduledJob
from asgard.models.user import User


class ScheduledJobsService:
    @staticmethod
    async def get_job_by_id(
        job_id: str, user: User, account: Account, backend: ScheduledJobsBackend
    ) -> Optional[ScheduledJob]:
        return await backend.get_job_by_id(job_id, user, account)

    @staticmethod
    async def list_jobs(
        user: User, account: Account, backend: ScheduledJobsBackend
    ) -> List[ScheduledJob]:
        return await backend.list_jobs(user, account)

    @staticmethod
    async def create_job(
        job: ScheduledJob,
        user: User,
        account: Account,
        backend: ScheduledJobsBackend,
    ) -> ScheduledJob:
        return await backend.create_job(job, user, account)
