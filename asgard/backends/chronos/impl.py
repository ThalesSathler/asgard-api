from typing import Optional, List

from asgard.backends.chronos.models.converters import (
    ChronosScheduledJobConverter,
)
from asgard.backends.jobs import ScheduledJobsBackend
from asgard.clients.chronos import ChronosClient
from asgard.conf import settings
from asgard.http.exceptions import HTTPNotFound
from asgard.models.account import Account
from asgard.models.job import ScheduledJob
from asgard.models.user import User


class ChronosScheduledJobsBackend(ScheduledJobsBackend):
    def __init__(self) -> None:
        self.client = ChronosClient(settings.SCHEDULED_JOBS_SERVICE_ADDRESS)

    async def get_job_by_id(
        self, job_id: str, user: User, account: Account
    ) -> Optional[ScheduledJob]:
        namespaced_job_id = f"{account.namespace}-{job_id}"
        try:
            chronos_job = await self.client.get_job_by_id(namespaced_job_id)
            if chronos_job:
                scheduled_job = ChronosScheduledJobConverter.to_asgard_model(
                    chronos_job
                )
                scheduled_job.remove_namespace(account)
                return scheduled_job
        except HTTPNotFound:
            return None
        return None

    async def list_jobs(
        self, user: User, account: Account
    ) -> List[ScheduledJob]:
        filter_prefix = f"{account.namespace}-"
        chronos_jobs = await self.client.search(name=filter_prefix)
        all_jobs = [
            ChronosScheduledJobConverter.to_asgard_model(job).remove_namespace(
                account
            )
            for job in chronos_jobs
            if job.name.startswith(filter_prefix)
        ]
        all_jobs.sort(key=lambda job: job.id)
        return all_jobs
