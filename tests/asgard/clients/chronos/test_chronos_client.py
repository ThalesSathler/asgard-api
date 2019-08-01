from base64 import b64encode

from aioresponses import aioresponses
from asynctest import TestCase
from yarl import URL

from asgard.clients.chronos.client import ChronosClient
from asgard.clients.chronos.models.job import ChronosJob
from tests.utils import with_json_fixture

MOCK_URL = "http://chronos"


class ChronosClientTest(TestCase):
    async def setUp(self):
        self.client = ChronosClient(url=MOCK_URL)
        self.user = "chronos"
        self.password = "secret"
        self.client_with_auth = ChronosClient(
            url=MOCK_URL, user=self.user, password=self.password
        )
        self.auth_string = f"{self.user}:{self.password}"
        auth_data = b64encode(self.auth_string.encode("utf8")).decode("utf8")

        self.auth_header = {"Authorization": f"Basic {auth_data}"}

    def assert_auth_header_present(self, rsps, method, url, auth_header):
        all_mock_request = rsps.requests.get((method.upper(), URL(url)))
        self.assertIsNotNone(all_mock_request)
        first_request = all_mock_request[0]
        self.assertEqual(auth_header, first_request.kwargs.get("headers"))

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_call_api_with_auth_encoded_if_provided(
        self, dev_job_fixture
    ):

        chronos_job = ChronosJob(**dev_job_fixture)
        with aioresponses() as rsps:
            rsps.get(
                "http://chronos/v1/scheduler/job/job-id",
                status=200,
                payload=chronos_job.dict(),
            )
            resp = await self.client_with_auth.get_job_by_id("job-id")
            self.assert_auth_header_present(
                rsps,
                "get",
                "http://chronos/v1/scheduler/job/job-id",
                self.auth_header,
            )
            self.assertEqual(chronos_job.dict(), resp.dict())

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_does_not_include_auth_header_if_no_auth_provided(
        self, dev_job_fixture
    ):
        chronos_job = ChronosJob(**dev_job_fixture)
        with aioresponses() as rsps:
            rsps.get(
                "http://chronos/v1/scheduler/job/job-id",
                status=200,
                payload=chronos_job.dict(),
            )
            resp = await self.client.get_job_by_id("job-id")
            self.assertEqual(chronos_job.dict(), resp.dict())
            self.assert_auth_header_present(
                rsps, "get", "http://chronos/v1/scheduler/job/job-id", None
            )

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_use_auth_data_on_search(self, dev_job_fixture):
        url = "http://chronos/v1/scheduler/jobs/search?name=job"
        chronos_job = ChronosJob(**dev_job_fixture)
        with aioresponses() as rsps:
            rsps.get(url, status=200, payload=[])
            resp = await self.client_with_auth.search(name="job")
            self.assert_auth_header_present(rsps, "get", url, self.auth_header)

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_use_auth_data_on_create(self, dev_job_fixture):
        url = "http://chronos/v1/scheduler/iso8601"
        job = ChronosJob(**dev_job_fixture)
        with aioresponses() as rsps:
            rsps.post(url, status=200, payload={})
            await self.client_with_auth.create_job(job)
            self.assert_auth_header_present(rsps, "post", url, self.auth_header)

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_use_auth_data_on_delete(self, dev_job_fixture):
        job = ChronosJob(**dev_job_fixture)
        url = f"http://chronos/v1/scheduler/job/{dev_job_fixture['name']}"
        with aioresponses() as rsps:
            rsps.delete(url, status=200, payload={})
            await self.client_with_auth.delete_job(job)
            self.assert_auth_header_present(
                rsps, "delete", url, self.auth_header
            )
