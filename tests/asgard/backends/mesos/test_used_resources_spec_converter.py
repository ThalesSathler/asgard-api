from asynctest import TestCase

from asgard.backends.mesos.models.converters import (
    MesosUsedResourcesSpecConverter,
)
from asgard.clients.mesos.models.spec import MesosUsedResourcesSpec
from tests.utils import with_json_fixture


class MesosUsedResourcesSpecConverterTest(TestCase):
    async def setUp(self):
        self.expected_used_resources_spec_dict = {
            "disk": 0.0,
            "mem": 1024.0,
            "cpus": 1.0,
        }

    @with_json_fixture(
        "agents/ead07ffb-5a61-42c9-9386-21b680597e6c-S12/info.json"
    )
    async def test_to_asgard_model(self, agent_fixture):
        mesos_used_resources_dict = agent_fixture["used_resources"]
        mesos_spec = MesosUsedResourcesSpec(**mesos_used_resources_dict)

        asgard_spec = MesosUsedResourcesSpecConverter.to_asgard_model(
            mesos_spec
        )
        self.assertEqual(
            self.expected_used_resources_spec_dict, asgard_spec.dict()
        )
