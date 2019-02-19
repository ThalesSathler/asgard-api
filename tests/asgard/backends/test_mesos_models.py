from asynctest import TestCase
from aioresponses import aioresponses


from asgard.backends.mesos import MesosTask
from asgard.backends.mesos import MesosAgent

from tests.utils import get_fixture, build_mesos_cluster


class MesosTaskTest(TestCase):
    async def test_transform_mesos_task_name_to_asgard_task_name(self):
        original_task_name = (
            "infra_scoutapp_mesos-master.a34109d3-2b99-11e9-a3c9-d2a7ebde729b"
        )
        self.assertEqual(
            "scoutapp_mesos-master.a34109d3-2b99-11e9-a3c9-d2a7ebde729b",
            MesosTask._transform_to_asgard_task_name(original_task_name),
        )


class MesosAgentTest(TestCase):
    async def setUp(self):
        self.agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S0"
        agent_info = get_fixture(f"agents/{self.agent_id}/info.json")
        self.agent = MesosAgent(**agent_info)

    async def test_tasks_list_from_one_app_tasks_running(self):
        slave_id = self.agent.id
        slave_address = f"http://{self.agent.hostname}:{self.agent.port}"
        slave_namespace = self.agent.attributes["owner"]
        with aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            build_mesos_cluster(rsps, self.agent_id)
            app_id = "infra/asgard/api"
            tasks = await self.agent.tasks(app_id=app_id)
            self.assertEqual(2, len(tasks))

            expected_task_names = [
                "infra_asgard_api.7e5d20eb-248a-11e9-91ea-024286d5b96a",
                "infra_asgard_api.323a6f04-1d75-11e9-91ea-024286d5b96a",
            ]
            self.assertEqual(expected_task_names, [task.name for task in tasks])

    async def test_tasks_list_from_one_app_no_tasks_running_on_agent(self):
        slave_id = self.agent.id
        slave_address = f"http://{self.agent.hostname}:{self.agent.port}"
        slave_namespace = self.agent.attributes["owner"]
        with aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            build_mesos_cluster(rsps, self.agent_id)
            app_id = "apps/http/myapp"
            tasks = await self.agent.tasks(app_id=app_id)
            self.assertEqual(0, len(tasks))
