from asynctest import TestCase

from asgard.backends.chronos.models.converters import (
    ChronosConstraintSpecConverter,
)
from asgard.clients.chronos.models.job import (
    ChronosConstraintSpec,
    ChronosConstraintSpecItem,
)
from asgard.models.spec.constraint import ConstraintSpec
from tests.utils import with_json_fixture


class ChronosConstraintSpecConverterTest(TestCase):
    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_to_asgard_model(self, chronos_job_fixture):
        chronos_constraint_list = chronos_job_fixture["constraints"]
        asgard_constraint_spec = ChronosConstraintSpecConverter.to_asgard_model(
            chronos_constraint_list
        )
        self.assertEqual(
            ["hostname:LIKE:10.0.0.1", "workload:LIKE:general"],
            asgard_constraint_spec,
        )

    async def test_to_client_model(self):
        asgard_constraint_list = [
            "workload:LIKE:general",
            "hostname:LIKE:10.0.0.1",
        ]
        chronos_constraint_spec = ChronosConstraintSpecConverter.to_client_model(
            asgard_constraint_list
        )
        self.assertEqual(
            [["workload", "LIKE", "general"], ["hostname", "LIKE", "10.0.0.1"]],
            chronos_constraint_spec,
        )
