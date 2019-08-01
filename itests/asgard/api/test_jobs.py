from http import HTTPStatus

from asgard.api import jobs
from asgard.api.resources import ErrorDetail, ErrorResource
from asgard.api.resources.jobs import (
    ScheduledJobResource,
    ScheduledJobsListResource,
    CreateScheduledJobResource,
)
from asgard.app import app
from asgard.backends.chronos.models.converters import (
    ChronosScheduledJobConverter,
)
from asgard.clients.chronos.models.job import ChronosJob
from asgard.models.account import Account
from asgard.models.user import User
from itests.util import (
    BaseTestCase,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY,
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

        account = Account(**ACCOUNT_INFRA_DICT)

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
            ).remove_namespace(account)
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

        account = Account(**ACCOUNT_DEV_DICT)

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
            ).remove_namespace(account),
            ChronosScheduledJobConverter.to_asgard_model(
                ChronosJob(**dev_with_infra_fixture)
            ).remove_namespace(account),
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

        account = Account(**ACCOUNT_DEV_DICT)

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
            ).remove_namespace(account),
            ChronosScheduledJobConverter.to_asgard_model(
                ChronosJob(**dev_with_infra_fixture)
            ).remove_namespace(account),
        ]

        resp_data = await resp.json()

        self.assertEqual(expected_asgard_jobs[0], resp_data["jobs"][0])
        self.assertEqual(expected_asgard_jobs[1], resp_data["jobs"][1])

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    async def test_create_job_on_alternate_account(self, dev_job_fixture):
        """
        Confirmar que podemos fazer POST /jobs?account_id=<id>
        o o job será criado com o namespace da account de id = <id>
        """

        await _cleanup_chronos()

        resp = await self.client.post(
            "/jobs",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            params={"account_id": ACCOUNT_INFRA_ID},
            json=ChronosScheduledJobConverter.to_asgard_model(
                ChronosJob(**dev_job_fixture)
            ).dict(),
        )
        self.assertEqual(HTTPStatus.CREATED, resp.status)
        resp_data = await resp.json()
        self.assertEqual(
            f"{dev_job_fixture['name']}",
            CreateScheduledJobResource(**resp_data).job.id,
        )

        resp_created_job = await self.client.get(
            f"/jobs/{dev_job_fixture['name']}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            params={"account_id": ACCOUNT_INFRA_ID},
        )
        self.assertEqual(HTTPStatus.OK, resp_created_job.status)

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    async def test_create_job_job_does_not_exist(self, dev_job_fixture):
        await _cleanup_chronos()

        account = Account(**ACCOUNT_DEV_DICT)

        asgard_job_no_namespace = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**dev_job_fixture)
        ).remove_namespace(account)

        resp = await self.client.post(
            "/jobs",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=asgard_job_no_namespace.dict(),
        )
        self.assertEqual(HTTPStatus.CREATED, resp.status)
        resp_data = await resp.json()
        self.assertEqual(
            f"{asgard_job_no_namespace.id}",
            CreateScheduledJobResource(**resp_data).job.id,
        )

        resp_created_job = await self.client.get(
            f"/jobs/{asgard_job_no_namespace.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(HTTPStatus.OK, resp_created_job.status)

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    async def test_create_job_duplicate_entity(self, dev_job_fixture):
        account = Account(**ACCOUNT_DEV_DICT)
        await _load_jobs_into_chronos(dev_job_fixture)

        asgard_job_sem_namespace = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**dev_job_fixture)
        ).remove_namespace(account)

        resp = await self.client.post(
            "/jobs",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=asgard_job_sem_namespace.dict(),
        )
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, resp.status)
        resp_data = await resp.json()
        expected_error_msg = (
            f"Scheduled job already exists: {asgard_job_sem_namespace.id}"
        )
        self.assertEqual(
            ErrorResource(errors=[ErrorDetail(msg=expected_error_msg)]),
            resp_data,
        )

    @with_json_fixture("scheduled-jobs/chronos/infra-some-scheduled-job.json")
    async def test_create_job_name_has_namespace_from_another_account(
        self, infra_job_fixture
    ):

        await _cleanup_chronos()

        account = Account(**ACCOUNT_DEV_DICT)

        asgard_job_no_namespace = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**infra_job_fixture)
        ).remove_namespace(account)

        resp = await self.client.post(
            "/jobs",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=asgard_job_no_namespace.dict(),
        )
        self.assertEqual(HTTPStatus.CREATED, resp.status)
        resp_data = await resp.json()
        self.assertEqual(
            f"{asgard_job_no_namespace.id}",
            CreateScheduledJobResource(**resp_data).job.id,
        )

        resp_created_job = await self.client.get(
            f"/jobs/{asgard_job_no_namespace.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(HTTPStatus.OK, resp_created_job.status)

    async def test_create_job_invalid_input(self):
        """
    Retornamos HTTPStatus.BAD_REQUEST caso a entrada não seja um JSON válido
    """

        account = Account(**ACCOUNT_DEV_DICT)

        resp = await self.client.post(
            "/jobs",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            data="{data",
        )
        self.assertEqual(HTTPStatus.BAD_REQUEST, resp.status)

    @with_json_fixture("scheduled-jobs/chronos/infra-some-scheduled-job.json")
    async def test_create_job_validation_error(self, infra_job_fixture):
        """
        Validamos que retornamos HTTPStatus.UNPROCESSABLE_ENTITY caso a entrada esteja incompleta
        """
        account = Account(**ACCOUNT_DEV_DICT)

        asgard_job_no_namespace = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**infra_job_fixture)
        ).remove_namespace(account)

        incomplete_asgard_job = asgard_job_no_namespace.dict()
        del incomplete_asgard_job["container"]

        resp = await self.client.post(
            "/jobs",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=incomplete_asgard_job,
        )
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, resp.status)
        resp_data = await resp.json()
        expected_error_msg = """1 validation error\ncontainer\n  field required (type=value_error.missing)"""
        self.assertEqual(
            ErrorResource(errors=[ErrorDetail(msg=expected_error_msg)]).dict(),
            resp_data,
        )

    async def test_update_job_with_required(self):
        resp = await self.client.put("/jobs/my-job-id")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, resp.status)

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_update_job_on_alternate_account(self, infra_job_fixture):
        """
        Confirmar que podemos fazer PUT /jobs?account_id=<id>
        o job será criado com o namespace da account de id = <id>
        """
        account = Account(**ACCOUNT_INFRA_DICT)
        await _load_jobs_into_chronos(infra_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**infra_job_fixture)
        )

        asgard_job.remove_namespace(account)
        self.assertEqual(asgard_job.cpus, infra_job_fixture["cpus"])
        self.assertEqual(asgard_job.mem, infra_job_fixture["mem"])

        asgard_job.cpus = 2
        asgard_job.mem = 2048

        resp = await self.client.put(
            f"/jobs/{asgard_job.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            params={"account_id": ACCOUNT_INFRA_ID},
            json=asgard_job.dict(),
        )
        self.assertEqual(HTTPStatus.ACCEPTED, resp.status)
        updated_job_response = await self.client.get(
            f"/jobs/{asgard_job.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            params={"account_id": ACCOUNT_INFRA_ID},
        )
        updated_job_data = await updated_job_response.json()
        updated_job_resource = CreateScheduledJobResource(**updated_job_data)
        self.assertEqual(asgard_job.cpus, updated_job_resource.job.cpus)
        self.assertEqual(asgard_job.mem, updated_job_resource.job.mem)

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    async def test_update_job_job_exist(self, dev_job_fixture):
        await _load_jobs_into_chronos(dev_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**dev_job_fixture)
        )

        asgard_job.remove_namespace(self.account)
        self.assertEqual(asgard_job.cpus, dev_job_fixture["cpus"])
        self.assertEqual(asgard_job.mem, dev_job_fixture["mem"])

        asgard_job.cpus = 2
        asgard_job.mem = 2048

        resp = await self.client.put(
            f"/jobs/{asgard_job.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=asgard_job.dict(),
        )
        self.assertEqual(HTTPStatus.ACCEPTED, resp.status)
        updated_job_response = await self.client.get(
            f"/jobs/{asgard_job.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        updated_job_data = await updated_job_response.json()
        updated_job_resource = CreateScheduledJobResource(**updated_job_data)
        self.assertEqual(asgard_job.cpus, updated_job_resource.job.cpus)
        self.assertEqual(asgard_job.mem, updated_job_resource.job.mem)

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    async def test_update_job_job_does_not_exist(self, dev_job_fixture):
        await _load_jobs_into_chronos(dev_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**dev_job_fixture)
        )

        asgard_job.id = "job-does-not-exist"
        asgard_job.remove_namespace(self.account)

        resp = await self.client.put(
            f"/jobs/{asgard_job.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=asgard_job.dict(),
        )
        self.assertEqual(HTTPStatus.NOT_FOUND, resp.status)
        self.assertEqual(
            ErrorResource(
                errors=[ErrorDetail(msg=f"Entity not found: {asgard_job.id}")]
            ).dict(),
            await resp.json(),
        )

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    async def test_update_job_name_has_namespace_from_another_account(
        self, dev_job_fixture
    ):
        """
        Mesmo que um job tenha o nome começado pelo namespace de outra conta,
        devemos atualizar o job da conta correta, que é a conta do usuário fazendo
        o request
        """
        self.maxDiff = None
        dev_job_fixture["name"] = f"dev-infra-{dev_job_fixture['name']}"
        await _load_jobs_into_chronos(dev_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**dev_job_fixture)
        )

        asgard_job.remove_namespace(self.account)
        self.assertEqual(asgard_job.cpus, dev_job_fixture["cpus"])
        self.assertEqual(asgard_job.mem, dev_job_fixture["mem"])

        asgard_job.cpus = 4
        asgard_job.mem = 512

        resp = await self.client.put(
            f"/jobs/{asgard_job.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=asgard_job.dict(),
        )
        self.assertEqual(HTTPStatus.ACCEPTED, resp.status)
        resp_data = await resp.json()

        asgard_job.add_constraint(f"owner:LIKE:{self.account.owner}")
        self.assertEqual(
            CreateScheduledJobResource(job=asgard_job).dict(), resp_data
        )

        updated_job_response = await self.client.get(
            f"/jobs/{asgard_job.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        updated_job_data = await updated_job_response.json()
        updated_job_resource = CreateScheduledJobResource(**updated_job_data)
        self.assertEqual(asgard_job.cpus, updated_job_resource.job.cpus)
        self.assertEqual(asgard_job.mem, updated_job_resource.job.mem)

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    async def test_update_job_invalid_input(self, dev_job_fixture):
        resp = await self.client.put(
            f"/jobs/some-invalid-job",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            data="{data",
        )
        self.assertEqual(HTTPStatus.BAD_REQUEST, resp.status)

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    async def test_update_job_validation_error(self, dev_job_fixture):
        asgard_job_no_namespace = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**dev_job_fixture)
        ).remove_namespace(self.account)

        incomplete_asgard_job = asgard_job_no_namespace.dict()
        del incomplete_asgard_job["container"]

        resp = await self.client.put(
            f"/jobs/{asgard_job_no_namespace.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=incomplete_asgard_job,
        )
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, resp.status)
        resp_data = await resp.json()
        expected_error_msg = """1 validation error\ncontainer\n  field required (type=value_error.missing)"""
        self.assertEqual(
            ErrorResource(errors=[ErrorDetail(msg=expected_error_msg)]).dict(),
            resp_data,
        )

    async def test_delete_job_auth_required(self):
        resp = await self.client.delete("/jobs/my-job-id")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, resp.status)

    @with_json_fixture("scheduled-jobs/chronos/dev-with-infra-in-name.json")
    async def test_delete_job_job_exist(self, dev_job_fixture):
        await _load_jobs_into_chronos(dev_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**dev_job_fixture)
        ).remove_namespace(self.account)

        resp = await self.client.delete(
            f"/jobs/{asgard_job.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(HTTPStatus.OK, resp.status)
        resp_data = await resp.json()
        self.assertEqual(ScheduledJobResource(job=asgard_job).dict(), resp_data)

        resp = await self.client.get(
            f"/jobs/{asgard_job.id}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(HTTPStatus.NOT_FOUND, resp.status)

    async def test_delete_job_job_does_not_exist(self):
        resp = await self.client.delete(
            f"/jobs/job-does-not-exist",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(HTTPStatus.NOT_FOUND, resp.status)
        resp_data = await resp.json()
        self.assertEqual(ScheduledJobResource().dict(), resp_data)
