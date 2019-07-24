import asyncio
from http import HTTPStatus

from asgard.api import jobs
from asgard.api.resources.jobs import (
    ScheduledJobResource,
    ScheduledJobsListResource,
)
from asgard.app import app
from asgard.backends.chronos.models.converters import (
    ChronosScheduledJobConverter,
)
from asgard.clients.chronos.models.job import ChronosJob
from asgard.conf import settings
from asgard.http.client import http_client
from asgard.models.account import Account
from asgard.models.user import User
from itests.util import (
    BaseTestCase,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    ACCOUNT_DEV_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY,
    USER_WITH_NO_ACCOUNTS_AUTH_KEY,
    ACCOUNT_INFRA_ID,
    _load_jobs_into_chronos,
    _cleanup_chronos,
)
from tests.utils import with_json_fixture


class JobsEndpointTestCase(BaseTestCase):
    async def setUp(self):
        await super(JobsEndpointTestCase, self).setUp()
        self.client = await self.aiohttp_client(app)
        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        self.account = Account(**ACCOUNT_DEV_DICT)

    async def tearDown(self):
        await super(JobsEndpointTestCase, self).tearDown()

    async def test_jobs_get_by_id_auth_required(self):
        resp = await self.client.get("/jobs/job-does-not-exist")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, resp.status)

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_jobs_get_by_id_job_exist(self, chronos_job_fixture):

        await _load_jobs_into_chronos(chronos_job_fixture)

        asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**chronos_job_fixture)
        )
        # A busca deve ser feita sempre *sem* o namespace
        asgard_job.remove_namespace(self.account)
        resp = await self.client.get(
            f"/jobs/{asgard_job.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(HTTPStatus.OK, resp.status)
        resp_data = await resp.json()
        self.assertEqual(ScheduledJobResource(job=asgard_job).dict(), resp_data)

    async def test_jobs_get_by_by_id_jobs_does_not_exist(self):
        resp = await self.client.get(
            "/jobs/job-does-not-exist",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(HTTPStatus.NOT_FOUND, resp.status)
        resp_data = await resp.json()
        self.assertEqual(ScheduledJobResource().dict(), resp_data)

    async def test_list_jobs_must_be_authenticated(self):
        resp = await self.client.get("/jobs")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, resp.status)

    async def test_list_jobs_empty_result(self):
        await _cleanup_chronos()
        resp = await self.client.get(
            "/jobs",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        resp_data = await resp.json()
        self.assertEqual(ScheduledJobsListResource(jobs=[]).dict(), resp_data)

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    @with_json_fixture("scheduled-jobs/chronos/infra-some-scheduled-job.json")
    async def test_list_jobs_do_not_include_jobs_from_alternate_account(
        self, dev_job_fixture, infra_job_fixture
    ):
        """
        Valida o parametro ?account_id=
        """
        await _load_jobs_into_chronos(dev_job_fixture, infra_job_fixture)

        resp = await self.client.get(
            "/jobs",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            params={"account_id": ACCOUNT_INFRA_ID},
        )
        self.assertEqual(HTTPStatus.OK, resp.status)

        expected_asgard_jobs = [
            ChronosScheduledJobConverter.to_asgard_model(
                ChronosJob(**infra_job_fixture)
            )
        ]

        resp_data = await resp.json()
        self.assertEqual(
            ScheduledJobsListResource(jobs=expected_asgard_jobs).dict(),
            resp_data,
        )

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    @with_json_fixture("scheduled-jobs/chronos/infra-some-scheduled-job.json")
    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    async def test_list_jobs_from_default_account(
        self, dev_another_job_fixture, infra_job_fixture, dev_with_infra_fixture
    ):
        await _load_jobs_into_chronos(
            dev_another_job_fixture, infra_job_fixture, dev_with_infra_fixture
        )

        resp = await self.client.get(
            "/jobs",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(HTTPStatus.OK, resp.status)

        expected_asgard_jobs = [
            ChronosScheduledJobConverter.to_asgard_model(
                ChronosJob(**dev_another_job_fixture)
            ),
            ChronosScheduledJobConverter.to_asgard_model(
                ChronosJob(**dev_with_infra_fixture)
            ),
        ]

        resp_data = await resp.json()
        self.assertEqual(
            ScheduledJobsListResource(jobs=expected_asgard_jobs).dict(),
            resp_data,
        )

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_list_jobs_return_ordered_by_name(
        self, dev_with_infra_fixture, dev_another_job_fixture
    ):

        await _load_jobs_into_chronos(
            dev_another_job_fixture, dev_with_infra_fixture
        )

        resp = await self.client.get(
            "/jobs",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(HTTPStatus.OK, resp.status)

        expected_asgard_jobs = [
            ChronosScheduledJobConverter.to_asgard_model(
                ChronosJob(**dev_another_job_fixture)
            ),
            ChronosScheduledJobConverter.to_asgard_model(
                ChronosJob(**dev_with_infra_fixture)
            ),
        ]

        resp_data = await resp.json()

        self.assertEqual(expected_asgard_jobs[0], resp_data["jobs"][0])
        self.assertEqual(expected_asgard_jobs[1], resp_data["jobs"][1])
