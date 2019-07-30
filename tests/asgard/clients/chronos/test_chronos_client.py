from base64 import b64encode
from http import HTTPStatus

from aioresponses import aioresponses
from asynctest import TestCase
from yarl import URL

from asgard.clients.chronos.client import ChronosClient
from asgard.clients.chronos.models.job import ChronosJob
from tests.utils import with_json_fixture


class ChronosClientTest(TestCase):
    async def setUp(self):
        self.client = ChronosClient(url="http://chronos")
        self.user = "chronos"
        self.password = "secret"
        self.auth_string = f"{self.user}:{self.password}"
        auth_data = b64encode(self.auth_string.encode("utf8")).decode("utf8")

        self.auth_header = {"Authorization": f"Basic {auth_data}"}

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_call_api_with_auth_encoded_if_provided(
        self, dev_job_fixture
    ):

        client = ChronosClient(
            url="http://chronos", user=self.user, password=self.password
        )
        chronos_job = ChronosJob(**dev_job_fixture)
        with aioresponses() as rsps:
            rsps.get(
                "http://chronos/v1/scheduler/job/job-id",
                status=200,
                payload=chronos_job.dict(),
            )
            resp = await client.get_job_by_id("job-id")
            all_mock_request = rsps.requests.get(
                ("GET", URL("http://chronos/v1/scheduler/job/job-id"))
            )
            self.assertIsNotNone(all_mock_request)
            first_request = all_mock_request[0]
            self.assertEqual(
                self.auth_header, first_request.kwargs.get("headers")
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
