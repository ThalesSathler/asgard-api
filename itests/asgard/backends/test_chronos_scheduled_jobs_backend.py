import asyncio

import aiohttp
from asynctest import TestCase
from asynctest.mock import CoroutineMock

from asgard.backends.chronos.impl import ChronosScheduledJobsBackend
from asgard.backends.chronos.models.converters import (
    ChronosScheduledJobConverter,
)
from asgard.clients.chronos import ChronosClient
from asgard.clients.chronos.models.job import ChronosJob
from asgard.conf import settings
from asgard.http.client import http_client
from asgard.models.account import Account
from asgard.models.user import User
from itests.util import (
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_DICT,
    _load_jobs_into_chronos,
)
from tests.utils import with_json_fixture


class ChronosScheduledJobsBackendTest(TestCase):
    async def setUp(self):
        self.backend = ChronosScheduledJobsBackend()

    async def test_get_job_by_id_job_not_found(self):
        job_id = "job-not-found"
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        job = await self.backend.get_job_by_id(job_id, user, account)
        self.assertIsNone(job)

    async def test_add_namespace_to_job_name(self):
        self.backend.client = CoroutineMock(spec=ChronosClient)
        self.backend.client.get_job_by_id.return_value = None

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        job_id = "my-scheduled-job"

        await self.backend.get_job_by_id(job_id, user, account)
        self.backend.client.get_job_by_id.assert_awaited_with(
            f"{account.namespace}-{job_id}"
        )

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_get_job_by_id_job_exists(self, job_fixture):
        job_fixture["name"] = "dev-scheduled-job"
        async with http_client as client:
            await client.post(
                f"{settings.SCHEDULED_JOBS_SERVICE_ADDRESS}/v1/scheduler/iso8601",
                json=job_fixture,
            )

        # Para dar tempo do chronos registra e responder no request log abaixo
        await asyncio.sleep(1)
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        job_id = "scheduled-job"

        job = await self.backend.get_job_by_id(job_id, user, account)
        self.assertEqual(job_id, job.id)

    async def test_get_job_by_id_service_unavailable(self):
        """
        Por enquanto deixamos o erro ser propagado.
        """
        get_job_by_id_mock = CoroutineMock(
            side_effect=aiohttp.ClientConnectionError()
        )
        self.backend.client = CoroutineMock(spec=ChronosClient)
        self.backend.client.get_job_by_id = get_job_by_id_mock

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        with self.assertRaises(aiohttp.ClientConnectionError):
            await self.backend.get_job_by_id("job-id", user, account)

    @with_json_fixture("scheduled-jobs/chronos/infra-some-scheduled-job.json")
    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_list_jobs_no_not_include_jobs_from_other_namespaces(
        self, infra_job_fixture, dev_job_fixture
    ):
        await _load_jobs_into_chronos(infra_job_fixture, dev_job_fixture)

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        jobs = await self.backend.list_jobs(user, account)

        expected_asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**dev_job_fixture)
        ).remove_namespace(account)
        self.assertCountEqual([expected_asgard_job], jobs)

    async def test_list_jobs_empty_result(self):
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        account.namespace = "namespace-does-not-have-any-jobs"
        jobs = await self.backend.list_jobs(user, account)

        self.assertCountEqual([], jobs)

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    @with_json_fixture("scheduled-jobs/chronos/infra-some-scheduled-job.json")
    async def test_list_jobs_do_not_include_jobs_from_another_ns_that_has_my_ns_in_name(
        self, dev_with_infra_job_fixture, infra_job_fixture
    ):
        """
        O Namespace só vale se estiver no ínicio do nome do job. Dado dois jobs:
         - asgard-curator-delete-indices-asgard-app-logs
         - infra-my-job-has-asgard-in-the-name

        Quando buscarmos os jobs namespace "asgard", temos que
        retornar apenas o primeiro.
        """
        await _load_jobs_into_chronos(
            dev_with_infra_job_fixture, infra_job_fixture
        )

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_INFRA_DICT)
        jobs = await self.backend.list_jobs(user, account)

        expected_asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**infra_job_fixture)
        ).remove_namespace(account)
        self.assertCountEqual([expected_asgard_job], jobs)
