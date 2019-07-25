from asynctest import TestCase
from asynctest.mock import CoroutineMock

from asgard.backends.jobs import ScheduledJobsBackend
from asgard.models.account import Account
from asgard.models.user import User
from asgard.services.jobs import ScheduledJobsService
from itests.util import USER_WITH_MULTIPLE_ACCOUNTS_DICT, ACCOUNT_DEV_DICT


class ScheduledJobsServiceTest(TestCase):
    async def setUp(self):
        self.backend = CoroutineMock(spec=ScheduledJobsBackend)

        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        self.account = Account(**ACCOUNT_DEV_DICT)

    async def test_get_job_by_id(self):

        await ScheduledJobsService.get_job_by_id(
            "my-id", self.user, self.account, self.backend
        )
        self.backend.get_job_by_id.assert_awaited_with(
            "my-id", self.user, self.account
        )

    async def test_list_jobs_from_account(self):

        await ScheduledJobsService.list_jobs(
            self.user, self.account, self.backend
        )
        self.backend.list_jobs.assert_awaited_with(self.user, self.account)

    async def test_create_job(self):
        job = CoroutineMock()

        await ScheduledJobsService.create_job(
            job, self.user, self.account, self.backend
        )
        self.backend.create_job.assert_awaited_with(
            job, self.user, self.account
        )
