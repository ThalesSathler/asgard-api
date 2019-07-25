import abc
from typing import Optional, List

from asgard.models.account import Account
from asgard.models.job import ScheduledJob
from asgard.models.user import User


class ScheduledJobsBackend(abc.ABC):
    @abc.abstractmethod
    async def get_job_by_id(
        self, job_id: str, user: User, account: Account
    ) -> Optional[ScheduledJob]:
        raise NotImplementedError

    @abc.abstractmethod
    async def list_jobs(
        self, user: User, account: Account
    ) -> List[ScheduledJob]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_job(
        self, job: ScheduledJob, user: User, account: Account
    ) -> ScheduledJob:
        raise NotImplementedError
