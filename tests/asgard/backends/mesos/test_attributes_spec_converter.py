from asynctest import TestCase

from asgard.backends.mesos.models.converters import MesosAttrbutesSpecConverter
from asgard.clients.mesos.models.spec import MesosAttributesSpec
from tests.utils import with_json_fixture


class MesosAttrbutesSpecConverterTest(TestCase):
    async def setUp(self):
        self.expected_attributes_spec_dict = {
            "mesos": "slave",
            "workload": "asgard-log-ingest-rabbitmq",
            "dc": "aws",
            "owner": "asgard",
        }

    @with_json_fixture(
        "agents/ead07ffb-5a61-42c9-9386-21b680597e6c-S12/info.json"
    )
    async def test_to_asgard_model(self, agent_fixture):
        mesos_used_resources_dict = agent_fixture["attributes"]
        mesos_spec: MesosAttributesSpec = dict(**mesos_used_resources_dict)

        asgard_spec = MesosAttrbutesSpecConverter.to_asgard_model(mesos_spec)
        self.assertEqual(self.expected_attributes_spec_dict, asgard_spec)
