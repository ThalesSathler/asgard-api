import asyncio
from base64 import b64encode
from http import HTTPStatus

import aiohttp
from aioresponses import aioresponses
from asynctest import TestCase
from asynctest.mock import CoroutineMock

from asgard.backends.chronos.impl import ChronosScheduledJobsBackend
from asgard.backends.chronos.models.converters import (
    ChronosScheduledJobConverter,
)
from asgard.clients.chronos import ChronosClient
from asgard.clients.chronos.models.job import ChronosJob
from asgard.conf import settings
from asgard.exceptions import DuplicateEntity, NotFoundEntity
from asgard.http.client import http_client
from asgard.http.exceptions import HTTPNotFound
from asgard.models.account import Account
from asgard.models.spec.fetch import FetchURLSpec
from asgard.models.user import User
from itests.util import (
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_DICT,
    _load_jobs_into_chronos,
    _cleanup_chronos,
)
from tests.utils import with_json_fixture, get_fixture


class ChronosScheduledJobsBackendTest(TestCase):
    async def setUp(self):
        self.backend = ChronosScheduledJobsBackend()

        self.chronos_dev_job_fixture = get_fixture(
            "scheduled-jobs/chronos/dev-with-infra-in-name.json"
        )

        self.asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**self.chronos_dev_job_fixture)
        )

        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        self.account = Account(**ACCOUNT_DEV_DICT)

    async def test_pass_auth_to_chronos_client(self):
        backend = ChronosScheduledJobsBackend()
        user, password = (
            settings.SCHEDULED_JOBS_SERVICE_AUTH.user,
            settings.SCHEDULED_JOBS_SERVICE_AUTH.password,
        )
        expected_auth_data = b64encode(
            f"{user}:{password}".encode("utf8")
        ).decode("utf8")
        self.assertEqual(expected_auth_data, backend.client.auth_data)

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

    async def test_create_job_job_does_not_exist(self):
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        await _cleanup_chronos()

        self.asgard_job.remove_namespace(self.account)
        returned_job = await self.backend.create_job(
            self.asgard_job, user, account
        )
        await asyncio.sleep(1)
        stored_job = await self.backend.get_job_by_id(
            returned_job.id, user, account
        )
        self.assertEqual(returned_job, stored_job)

    async def test_create_job_add_default_uris_fields(self):
        """
        Confere que as URIs default são adicionadas ao Job
        """
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        expected_fetch_list = self.asgard_job.fetch + [
            FetchURLSpec(uri=settings.SCHEDULED_JOBS_DEFAULT_FETCH_URIS[0].uri),
            FetchURLSpec(uri=settings.SCHEDULED_JOBS_DEFAULT_FETCH_URIS[1].uri),
        ]

        await _cleanup_chronos()

        self.asgard_job.remove_namespace(self.account)
        returned_job = await self.backend.create_job(
            self.asgard_job, user, account
        )
        await asyncio.sleep(1)
        stored_job = await self.backend.get_job_by_id(
            returned_job.id, user, account
        )
        self.assertEqual(expected_fetch_list, stored_job.fetch)

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    @with_json_fixture("scheduled-jobs/chronos/infra-some-scheduled-job.json")
    async def test_create_job_duplicate_entity(
        self, dev_job_fixture, infra_job_fixture
    ):
        """
        Se tentarmos criar um job com o mesmo nome de um que já existe,
        lançamos DuplicateEntity exception. Para atualizar um job temos
        um método separado
        """

        await _load_jobs_into_chronos(dev_job_fixture)
        infra_job_fixture["name"] = dev_job_fixture["name"]

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**infra_job_fixture)
        )

        asgard_job.remove_namespace(account)
        with self.assertRaises(DuplicateEntity):
            await self.backend.create_job(asgard_job, user, account)

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    @with_json_fixture("scheduled-jobs/chronos/infra-some-scheduled-job.json")
    async def test_create_job_name_has_namespace_from_another_account(
        self, dev_job_fixture, infra_job_fixture
    ):
        """
        Mesmo que o nome do job começe com o namespace de outra conta, o registro
        do novo job deve ser feito na conta correta
        """

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        await _load_jobs_into_chronos(dev_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**infra_job_fixture)
        )

        returned_job = await self.backend.create_job(asgard_job, user, account)
        await asyncio.sleep(1)
        stored_job = await self.backend.get_job_by_id(
            returned_job.id, user, account
        )
        self.assertEqual(returned_job, stored_job)

    async def test_create_job_add_owner_constraint(self,):
        """
        Todos os Jobs criados recebem a constraint `owner:LIKE:{account.owner}`
        """
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        await _cleanup_chronos()

        returned_job = await self.backend.create_job(
            self.asgard_job, user, account
        )
        stored_job = await self.backend.get_job_by_id(
            returned_job.id, user, account
        )
        self.assertCountEqual(
            [
                "hostname:LIKE:10.0.0.1",
                "workload:LIKE:general",
                f"owner:LIKE:{account.owner}",
            ],
            stored_job.constraints,
        )

    async def test_create_job_force_owner_constraint_if_already_exist(self):
        """
        Mesmo se o Job sendo criado já tiver a constraint `owner:LIKE:...` temos
        que substituir por `owner:LIKE:{account.owner}`
        """
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        await _cleanup_chronos()
        self.asgard_job.add_constraint("owner:LIKE:other-value")

        returned_job = await self.backend.create_job(
            self.asgard_job, user, account
        )
        stored_job = await self.backend.get_job_by_id(
            returned_job.id, user, account
        )
        self.assertCountEqual(
            [
                "hostname:LIKE:10.0.0.1",
                "workload:LIKE:general",
                f"owner:LIKE:{account.owner}",
            ],
            stored_job.constraints,
        )

    async def test_update_job_job_does_not_exist(self):
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        await _cleanup_chronos()

        with self.assertRaises(NotFoundEntity):
            await self.backend.update_job(self.asgard_job, user, account)

    async def test_update_job_change_root_fields(self):
        await _load_jobs_into_chronos(self.chronos_dev_job_fixture)

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        self.asgard_job._remove_constraint_by_name("owner")
        self.asgard_job.remove_namespace(account)

        self.asgard_job.cpus = 2
        self.asgard_job.mem = 1024
        self.asgard_job.description = "Minha description"
        self.asgard_job.retries = 4

        updated_job = await self.backend.update_job(
            self.asgard_job, user, account
        )

        stored_job = await self.backend.get_job_by_id(
            updated_job.id, user, account
        )
        self.assertEqual(self.asgard_job.cpus, stored_job.cpus)
        self.assertEqual(self.asgard_job.mem, stored_job.mem)
        self.assertEqual(self.asgard_job.description, stored_job.description)
        self.assertEqual(self.asgard_job.retries, stored_job.retries)

    async def test_update_job_add_fetch_uri(self):
        await _load_jobs_into_chronos(self.chronos_dev_job_fixture)
        new_fetch_uri = FetchURLSpec(
            uri="https://static.server.com/assets/main.css"
        )
        self.asgard_job.fetch.append(new_fetch_uri)

        self.asgard_job.remove_namespace(self.account)
        await self.backend.update_job(self.asgard_job, self.user, self.account)

        stored_job = await self.backend.get_job_by_id(
            self.asgard_job.id, self.user, self.account
        )
        self.assertCountEqual(self.asgard_job.fetch, stored_job.fetch)

    async def test_update_job_add_default_fetch_uri(self):
        del self.chronos_dev_job_fixture["fetch"]

        new_fetch_uri = FetchURLSpec(
            uri="https://static.server.com/assets/main.css"
        )

        expected_fetch_list = [
            new_fetch_uri,
            FetchURLSpec(uri=settings.SCHEDULED_JOBS_DEFAULT_FETCH_URIS[0].uri),
            FetchURLSpec(uri=settings.SCHEDULED_JOBS_DEFAULT_FETCH_URIS[1].uri),
        ]

        await _load_jobs_into_chronos(self.chronos_dev_job_fixture)

        asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**self.chronos_dev_job_fixture)
        )
        asgard_job.add_fetch_uri(new_fetch_uri)
        asgard_job.remove_namespace(self.account)

        await self.backend.update_job(asgard_job, self.user, self.account)

        stored_job = await self.backend.get_job_by_id(
            asgard_job.id, self.user, self.account
        )
        self.assertEqual(expected_fetch_list, stored_job.fetch)

    async def test_update_job_change_sub_fields(self):
        await _load_jobs_into_chronos(self.chronos_dev_job_fixture)

        self.asgard_job.remove_namespace(self.account)
        self.asgard_job.container.pull_image = True
        self.asgard_job.container.image = "asgard-api:latest"
        self.asgard_job.container.parameters = None
        await self.backend.update_job(self.asgard_job, self.user, self.account)

        stored_job = await self.backend.get_job_by_id(
            self.asgard_job.id, self.user, self.account
        )
        self.assertCountEqual(self.asgard_job.dict(), stored_job.dict())

    async def test_update_job_remove_command(self):
        await _load_jobs_into_chronos(self.chronos_dev_job_fixture)

        self.asgard_job.remove_namespace(self.account)
        self.asgard_job.command = None
        await self.backend.update_job(self.asgard_job, self.user, self.account)

        stored_job = await self.backend.get_job_by_id(
            self.asgard_job.id, self.user, self.account
        )
        self.assertCountEqual(self.asgard_job.dict(), stored_job.dict())

    async def test_update_job_remove_arguments(self):
        await _load_jobs_into_chronos(self.chronos_dev_job_fixture)

        self.asgard_job.remove_namespace(self.account)
        self.asgard_job.arguments = None
        await self.backend.update_job(self.asgard_job, self.user, self.account)

        stored_job = await self.backend.get_job_by_id(
            self.asgard_job.id, self.user, self.account
        )
        self.assertCountEqual(self.asgard_job.dict(), stored_job.dict())

    async def test_update_job_add_owner_constraint(self):
        await _load_jobs_into_chronos(self.chronos_dev_job_fixture)

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        self.asgard_job._remove_constraint_by_name("owner")
        self.asgard_job.remove_namespace(account)
        self.assertCountEqual(
            ["hostname:LIKE:10.0.0.1", "workload:LIKE:general"],
            self.asgard_job.constraints,
        )
        updated_job = await self.backend.update_job(
            self.asgard_job, user, account
        )
        self.assertCountEqual(
            [
                "hostname:LIKE:10.0.0.1",
                "workload:LIKE:general",
                f"owner:LIKE:{account.owner}",
            ],
            updated_job.constraints,
        )

    async def test_delete_job_job_does_not_exist(self):
        await _cleanup_chronos()
        job_not_found = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**self.chronos_dev_job_fixture)
        )
        job_not_found.id = "this-job-does-not-exist"
        with self.assertRaises(NotFoundEntity):
            await self.backend.delete_job(
                job_not_found, self.user, self.account
            )

    async def test_delete_job_job_exists(self):
        await _load_jobs_into_chronos(self.chronos_dev_job_fixture)
        self.asgard_job.remove_namespace(self.account)

        deleted_job = await self.backend.delete_job(
            self.asgard_job, self.user, self.account
        )
        self.assertEqual(self.asgard_job.dict(), deleted_job.dict())
        not_found_job = await self.backend.get_job_by_id(
            self.asgard_job.id, self.user, self.account
        )
        self.assertIsNone(not_found_job)

    async def test_delete_job_exist_when_get_does_not_exist_when_delete(self):
        """
        A lógica do delete é:
           get_by_id()
           se não existe, retorna Erro
           se existe, apaga.

        Esse teste valida que, se o job for removido *entre* as chamadas do get_by_id() e o delete(), ainda assim conseguimos retornar com se o job tivesse sido removido por nós.
        """
        self.asgard_job.remove_namespace(self.account)

        CHRONOS_BASE_URL = (
            f"{settings.SCHEDULED_JOBS_SERVICE_ADDRESS}/v1/scheduler"
        )

        with aioresponses() as rsps:
            rsps.get(
                f"{CHRONOS_BASE_URL}/job/{self.chronos_dev_job_fixture['name']}",
                payload=self.chronos_dev_job_fixture,
            )
            rsps.get(
                f"{CHRONOS_BASE_URL}/job/{self.chronos_dev_job_fixture['name']}",
                exception=HTTPNotFound(request_info=None),
            )
            rsps.delete(
                f"{CHRONOS_BASE_URL}/job/{self.chronos_dev_job_fixture['name']}",
                status=HTTPStatus.BAD_REQUEST,
            )

            deleted_job = await self.backend.delete_job(
                self.asgard_job, self.user, self.account
            )
            self.assertEqual(self.asgard_job.dict(), deleted_job.dict())
            not_found_job = await self.backend.get_job_by_id(
                self.asgard_job.id, self.user, self.account
            )
            self.assertIsNone(not_found_job)
