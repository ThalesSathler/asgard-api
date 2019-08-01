from asynctest import TestCase
from pydantic import ValidationError

from asgard.backends.chronos.models.converters import (
    ChronosScheduledJobConverter,
)
from asgard.clients.chronos.models.job import ChronosJob
from asgard.models.account import Account
from asgard.models.job import ScheduledJob
from itests.util import ACCOUNT_DEV_DICT
from tests.utils import with_json_fixture, get_fixture


class ScheduledJobModelTest(TestCase):
    async def setUp(self):
        self.container_spec = {"image": "alpine:3", "network": "BRIDGE"}
        self.schedule_spec = {
            "value": "20190811T2100+00:00/R",
            "tz": "America/Sao_Paulo",
        }

        self.required_fields_scheduled_job = {
            "id": "my-sheduled-app",
            "cpus": 5.0,
            "mem": 512,
            "container": {**self.container_spec},
            "schedule": self.schedule_spec,
            "description": "A Scheduled Task",
        }
        dev_chronos_job_fixture = get_fixture(
            "scheduled-jobs/chronos/dev-another-job.json"
        )
        self.asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**dev_chronos_job_fixture)
        )

    async def test_serialized_parse_dict_required_fields(self):
        full_scheduled_job = {
            **self.required_fields_scheduled_job,
            "command": None,
            "arguments": None,
            "concurrent": True,
            "disk": 0,
            "container": {
                **self.container_spec,
                "parameters": None,
                "privileged": False,
                "pull_image": True,
                "volumes": None,
                "ports": None,
                "type": "DOCKER",
            },
            "schedule": {**self.schedule_spec},
            "env": None,
            "constraints": None,
            "fetch": None,
            "shell": False,
            "retries": 5,
            "enabled": True,
        }
        self.assertEqual(
            full_scheduled_job, ScheduledJob(**full_scheduled_job).dict()
        )

    async def test_valid_job_name(self):
        """
        O nome de cada job so poderá ter [a-z0-9-]
        """
        self.required_fields_scheduled_job["id"] = "a-valid-name-2"
        job = ScheduledJob(**self.required_fields_scheduled_job)
        self.assertEqual(self.required_fields_scheduled_job["id"], job.id)

    async def test_invalid_job_name(self):
        with self.assertRaises(ValidationError):
            self.required_fields_scheduled_job["id"] = "InvalidJobName"
            ScheduledJob(**self.required_fields_scheduled_job)

    async def test_invalid_job_name_with_slash(self):
        with self.assertRaises(ValidationError):
            self.required_fields_scheduled_job["id"] = "my/app"
            ScheduledJob(**self.required_fields_scheduled_job)

    async def test_remove_account_namespace_app_id_does_not_have_namespace(
        self
    ):
        app = ScheduledJob(**self.required_fields_scheduled_job)
        account = Account(**ACCOUNT_DEV_DICT)
        self.assertEqual(self.required_fields_scheduled_job["id"], app.id)

        app.remove_namespace(account)
        self.assertEqual(self.required_fields_scheduled_job["id"], app.id)

    async def test_remove_namespace_only_once(self):
        account = Account(**ACCOUNT_DEV_DICT)
        self.required_fields_scheduled_job[
            "id"
        ] = f"{account.namespace}-{account.namespace}-my-app-with-ns"
        app = ScheduledJob(**self.required_fields_scheduled_job)

        app.remove_namespace(account)
        expected_app_id = f"{account.namespace}-my-app-with-ns"
        self.assertEqual(expected_app_id, app.id)

    async def test_remove_namepace_returns_self(self):

        account = Account(**ACCOUNT_DEV_DICT)
        self.required_fields_scheduled_job[
            "id"
        ] = f"my-app-with-{account.namespace}-ns"
        app = ScheduledJob(**self.required_fields_scheduled_job)

        returned_app = app.remove_namespace(account)
        self.assertTrue(app is returned_app)

    async def test_remove_namespace_app_id_contains_namespace(self):
        """
        Se o namepspace está no meio do nome, não deve ser removido
        """
        account = Account(**ACCOUNT_DEV_DICT)
        self.required_fields_scheduled_job[
            "id"
        ] = f"my-app-with-{account.namespace}-ns"
        app = ScheduledJob(**self.required_fields_scheduled_job)

        app.remove_namespace(account)
        self.assertEqual(self.required_fields_scheduled_job["id"], app.id)

    async def test_remove_namespace_app_id_begins_with_and_has_namespace_in_name(
        self
    ):
        account = Account(**ACCOUNT_DEV_DICT)
        self.required_fields_scheduled_job[
            "id"
        ] = f"{account.namespace}-my-app-with-{account.namespace}-ns"
        app = ScheduledJob(**self.required_fields_scheduled_job)

        app.remove_namespace(account)
        expected_app_id = f"my-app-with-{account.namespace}-ns"
        self.assertEqual(expected_app_id, app.id)

    async def test_remove_namespace_app_id_begins_with_namespace(self):
        account = Account(**ACCOUNT_DEV_DICT)
        self.required_fields_scheduled_job[
            "id"
        ] = f"{account.namespace}-my-app-with-ns"
        app = ScheduledJob(**self.required_fields_scheduled_job)

        app.remove_namespace(account)
        expected_app_id = "my-app-with-ns"
        self.assertEqual(expected_app_id, app.id)

    async def test_add_account_namespace_to_name(self):
        app = ScheduledJob(**self.required_fields_scheduled_job)
        account = Account(**ACCOUNT_DEV_DICT)
        self.assertEqual(self.required_fields_scheduled_job["id"], app.id)

        app.add_namespace(account)
        expected_app_id = (
            f"{account.namespace}-{self.required_fields_scheduled_job['id'] }"
        )
        self.assertEqual(expected_app_id, app.id)

    async def test_add_namespace_app_id_begins_with_namespace(self):
        """
        Adicionamos o namespace independente da app já ter o nome com
        exatamente o namespace no começo.
        """
        app = ScheduledJob(**self.required_fields_scheduled_job)
        account = Account(**ACCOUNT_DEV_DICT)
        self.assertEqual(self.required_fields_scheduled_job["id"], app.id)

        app.add_namespace(account)
        app.add_namespace(account)
        expected_app_id = f"{account.namespace}-{account.namespace }-{self.required_fields_scheduled_job['id']}"
        self.assertEqual(expected_app_id, app.id)

    async def test_add_namespace_app_id_has_namespace_in_the_middle(self):
        account = Account(**ACCOUNT_DEV_DICT)
        self.required_fields_scheduled_job[
            "id"
        ] = f"my-app-with-{account.namespace}-ns"
        app = ScheduledJob(**self.required_fields_scheduled_job)

        app.add_namespace(account)
        expected_app_id = (
            f"{account.namespace}-{self.required_fields_scheduled_job['id'] }"
        )
        self.assertEqual(expected_app_id, app.id)

    async def test_add_constraint_does_not_exist_yet(self,):
        self.asgard_job.add_constraint("dc:LIKE:aws")
        self.assertCountEqual(
            ["hostname:LIKE:10.0.0.1", "workload:LIKE:general", "dc:LIKE:aws"],
            self.asgard_job.constraints,
        )

    async def test_add_first_constraint(self,):
        self.asgard_job.constraints = None

        self.asgard_job.add_constraint("dc:LIKE:aws")
        self.assertCountEqual(["dc:LIKE:aws"], self.asgard_job.constraints)

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_add_multiple_constraints_builder_style(
        self, dev_chronos_job_fixture
    ):
        """
        Confirmamos que podemos fazer:
            job.add_constraint(...)
               .add_constraint(...)
        """
        del dev_chronos_job_fixture["constraints"]

        asgard_job = ChronosScheduledJobConverter.to_asgard_model(
            ChronosJob(**dev_chronos_job_fixture)
        )

        self.assertIsNone(asgard_job.constraints)

        asgard_job.add_constraint("dc:LIKE:aws").add_constraint(
            "workload:LIKE:general"
        )
        self.assertCountEqual(
            ["dc:LIKE:aws", "workload:LIKE:general"], asgard_job.constraints
        )

    @with_json_fixture("scheduled-jobs/chronos/dev-another-job.json")
    async def test_add_constraint_already_exist(self, dev_chronos_job_fixture):
        """
        Se a constraint já existir, temos que substituir.
        """

        self.assertCountEqual(
            ["hostname:LIKE:10.0.0.1", "workload:LIKE:general"],
            self.asgard_job.constraints,
        )
        self.asgard_job.add_constraint("hostname:LIKE:127.0.0.1")
        self.assertCountEqual(
            ["hostname:LIKE:127.0.0.1", "workload:LIKE:general"],
            self.asgard_job.constraints,
        )

    async def test_remove_constraint_by_name(self):
        self.assertCountEqual(
            ["hostname:LIKE:10.0.0.1", "workload:LIKE:general"],
            self.asgard_job.constraints,
        )
        self.asgard_job._remove_constraint_by_name("hostname")
        self.assertCountEqual(
            ["workload:LIKE:general"], self.asgard_job.constraints
        )

    async def test_remove_constraint_by_name_constraint_does_not_exist(self):
        self.assertCountEqual(
            ["hostname:LIKE:10.0.0.1", "workload:LIKE:general"],
            self.asgard_job.constraints,
        )
        self.asgard_job._remove_constraint_by_name("dc")
        self.assertCountEqual(
            ["hostname:LIKE:10.0.0.1", "workload:LIKE:general"],
            self.asgard_job.constraints,
        )

    async def test_remove_multiple_constraint_builder_style(self):
        self.assertCountEqual(
            ["hostname:LIKE:10.0.0.1", "workload:LIKE:general"],
            self.asgard_job.constraints,
        )
        self.asgard_job._remove_constraint_by_name(
            "dc"
        )._remove_constraint_by_name("hostname")
        self.assertCountEqual(
            ["workload:LIKE:general"], self.asgard_job.constraints
        )

    async def test_test_remove_more_constraints_that_job_has(self):
        """
        Podemos remover mesmo com a lista e constraints vazia, nesse caso
        a remoção é um no-op
        """
        self.assertCountEqual(
            ["hostname:LIKE:10.0.0.1", "workload:LIKE:general"],
            self.asgard_job.constraints,
        )
        self.asgard_job._remove_constraint_by_name(
            "dc"
        )._remove_constraint_by_name("hostname")._remove_constraint_by_name(
            "workload"
        )._remove_constraint_by_name(
            "rack"
        )
        self.assertCountEqual([], self.asgard_job.constraints)
