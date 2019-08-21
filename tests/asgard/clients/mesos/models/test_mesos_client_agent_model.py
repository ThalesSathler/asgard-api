from asynctest import TestCase

from asgard.backends.mesos.models.agent import MesosAgent
from asgard.clients.mesos.models.agent import MesosAgent as MesosClientAgent


class AgentModelTest(TestCase):
    async def test_trasnforms_to_asgard_mesos_agent_model(self):
        data = {
            "id": "4783cf15-4fb1-4c75-90fe-44eeec5258a7-S12",
            "hostname": "10.234.172.35",
            "port": 5051,
            "attributes": {"workload": "general", "owner": "asgard"},
            "registered_time": 1_550_246_118.23637,
            "resources": {
                "disk": 44326.0,
                "mem": 2920.0,
                "gpus": 0.0,
                "cpus": 2.0,
                "ports": "[31000-32000]",
            },
            "used_resources": {
                "disk": 0.0,
                "mem": 1024.0,
                "gpus": 0.0,
                "cpus": 1.0,
            },
            "active": True,
            "version": "1.4.1",
        }
        mesos_client_agent = MesosClientAgent(**data)
        asgard_mesos_agent = mesos_client_agent.to_asgard_model(MesosAgent)
        self.assertTrue(isinstance(asgard_mesos_agent, MesosAgent))
        self.assertEqual(
            "4783cf15-4fb1-4c75-90fe-44eeec5258a7-S12", asgard_mesos_agent.id
        )
        self.assertEqual("10.234.172.35", asgard_mesos_agent.hostname)
        self.assertEqual(True, asgard_mesos_agent.active)
        self.assertEqual("1.4.1", asgard_mesos_agent.version)
        self.assertEqual(5051, asgard_mesos_agent.port)
        self.assertEqual(
            {
                "disk": "44326.0",
                "mem": "2920.0",
                "gpus": "0.0",
                "cpus": "2.0",
                "ports": "[31000-32000]",
            },
            asgard_mesos_agent.resources,
        )
        self.assertEqual(
            {"disk": "0.0", "mem": "1024.0", "gpus": "0.0", "cpus": "1.0"},
            asgard_mesos_agent.used_resources,
        )
        self.assertEqual(
            {"workload": "general", "owner": "asgard"},
            asgard_mesos_agent.attributes,
        )
