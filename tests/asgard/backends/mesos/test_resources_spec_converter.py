from asynctest import TestCase

from asgard.backends.mesos.models.converters import MesosResourcesSpecConverter
from asgard.clients.mesos.models.spec import MesosResourcesSpec
from tests.utils import with_json_fixture


class MesosResourcesSpecConverterTest(TestCase):
    async def setUp(self):
        self.expected_resources_spec_dict = {
            "disk": 26877,
            "mem": 2560.0,
            "cpus": 2.5,
        }

    @with_json_fixture(
        "agents/ead07ffb-5a61-42c9-9386-21b680597e6c-S12/info.json"
    )
    async def test_to_asgard_model(self, agent_fixture):
        mesos_resources_dict = agent_fixture["resources"]
        mesos_spec = MesosResourcesSpec(**mesos_resources_dict)

        asgard_spec = MesosResourcesSpecConverter.to_asgard_model(mesos_spec)
        self.assertEqual(self.expected_resources_spec_dict, asgard_spec.dict())
