from asynctest import TestCase

from asgard.backends.mesos.models.agent import MesosAgent
from asgard.backends.mesos.models.converters import MesosAgentConverter
from asgard.clients.mesos.models.agent import MesosAgent as MesosClientAgent
from tests.utils import with_json_fixture


class AgentModelTest(TestCase):
    async def setUp(self):
        self.expected_asgard_agent_dict = {
            "id": "ead07ffb-5a61-42c9-9386-21b680597e6c-S44",
            "hostname": "172.18.0.18",
            "port": 5051,
            "attributes": {
                "mesos": "slave",
                "workload": "general",
                "dc": "aws",
                "owner": "dev",
            },
            "resources": {"disk": "26877.0", "mem": "2560.0", "cpus": "2.5"},
            "used_resources": {
                "disk": "0.0",
                "mem": "660.224",
                "cpus": "0.968",
            },
            "active": True,
            "version": "1.4.1",
        }

    @with_json_fixture(
        "agents/ead07ffb-5a61-42c9-9386-21b680597e6c-S44/info.json"
    )
    async def test_to_asgard_model_all_fields(self, agent_fixture):
        """
        Confere apenas os campos não-compostos.
        """
        mesos_agent = MesosClientAgent(**agent_fixture)
        asgard_agent = MesosAgentConverter.to_asgard_model(mesos_agent)
        self.assertEqual(
            {
                "type": "MESOS",
                "errors": {},
                "applications": [],
                "stats": {},
                "total_apps": 0,
                **self.expected_asgard_agent_dict,
            },
            asgard_agent.dict(),
        )
