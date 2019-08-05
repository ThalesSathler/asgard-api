from asynctest import TestCase

from asgard.backends.chronos.models.converters import (
    ChronosContainerParameterSpecConverter,
)
from asgard.clients.chronos.models.job import ChronosContainerParameterSpec
from asgard.models.spec.container import ContainerParameterSpec
from tests.utils import with_json_fixture


class TestContainerParameterSpecConverter(TestCase):
    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model(self, chronos_scheduled_job_fixture):
        chronos_container_param = ChronosContainerParameterSpec(
            **chronos_scheduled_job_fixture["container"]["parameters"][0]
        )
        asgard_container_param = ChronosContainerParameterSpecConverter.to_asgard_model(
            chronos_container_param
        )
        self.assertEqual(
            {"name": "a-docker-option", "value": "a-docker-value"},
            asgard_container_param.dict(),
        )

    async def test_convert_to_client_model(self):
        asgard_container_param = ContainerParameterSpec(
            name="dns", value="10.0.0.1"
        )
        chronos_container_param = ChronosContainerParameterSpecConverter.to_client_model(
            asgard_container_param
        )
        self.assertEqual(
            {"key": "dns", "value": "10.0.0.1"}, chronos_container_param.dict()
        )
