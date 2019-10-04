from aioresponses import aioresponses
from asynctest import TestCase, skip

from asgard.clients.mesos.client import MesosClient
from asgard.clients.mesos.models.agent import MesosAgent
from asgard.conf import settings
from tests.utils import build_mesos_cluster, get_fixture


class MesosClientTestCase(TestCase):
    async def setUp(self):
        self.mesos_client = MesosClient(*settings.MESOS_API_URLS)

    async def test_mesos_client_get_agent_by_id_check_all_fields(self):
        agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S0"
        async with MesosClient(*settings.MESOS_API_URLS) as mesos:
            with aioresponses() as rsps:
                build_mesos_cluster(rsps, agent_id)

                agent = await mesos.get_agent_by_id(agent_id=agent_id)
                self.assertTrue(isinstance(agent, MesosAgent))
                self.assertEqual(agent_id, agent.id)
                self.assertEqual(
                    {
                        "mesos": "slave",
                        "workload": "general",
                        "dc": "gcp",
                        "owner": "asgard-infra",
                    },
                    agent.attributes,
                )
                self.assertEqual("172.18.0.51", agent.hostname)
                self.assertEqual(5051, agent.port)
                self.assertEqual(True, agent.active)
                self.assertEqual("1.4.1", agent.version)
                self.assertEqual(
                    {
                        "disk": 0.0,
                        "mem": 1724.032,
                        "gpus": 0.0,
                        "cpus": 1.374,
                        "ports": "[31000-32000]",
                    },
                    agent.used_resources.dict(),
                )
                self.assertEqual(
                    {
                        "disk": 26877.0,
                        "mem": 2560.0,
                        "gpus": 0.0,
                        "cpus": 2.5,
                        "ports": "[30000-31999]",
                    },
                    agent.resources.dict(),
                )

    async def test_mesos_client_get_agents(self):
        """
        Retorna a lista de agents do cluster mesos
        """
        agent_ids = [
            "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",
            "ead07ffb-5a61-42c9-9386-21b680597e6c-S10",
            "ead07ffb-5a61-42c9-9386-21b680597e6c-S4",
            "ead07ffb-5a61-42c9-9386-21b680597e6c-S9",
        ]
        async with MesosClient(*settings.MESOS_API_URLS) as mesos:
            with aioresponses() as rsps:
                build_mesos_cluster(rsps, *agent_ids)
                agents = await mesos.get_agents()
                self.assertEquals(4, len(agents))
                self.assertEqual(agent_ids, [agent.id for agent in agents])

    async def test_mesos_client_get_agents_empty_cluster(self):
        """
        Retorna a lista de agents do cluster mesos
        """
        async with MesosClient(*settings.MESOS_API_URLS) as mesos:
            with aioresponses() as rsps:
                build_mesos_cluster(rsps)
                agents = await mesos.get_agents()
                self.assertEquals(0, len(agents))

    async def test_mesos_client_get_agent_by_id_agent_not_found(self):
        agent_id = "agent-not-found"
        async with MesosClient(*settings.MESOS_API_URLS) as mesos:
            with aioresponses() as rsps:
                rsps.get(
                    f"{settings.MESOS_API_URLS[0]}/slaves?slave_id={agent_id}",
                    status=200,
                    payload={"slaves": [], "recovered_slaves": []},
                )

                agent = await mesos.get_agent_by_id(agent_id=agent_id)
                self.assertIsNone(agent)

    @skip("")
    async def test_mesos_client_detect_leader_change(self):
        """
        Sempre faremos o request em qualquer das URLs dos master,
        mas vamos olhar se houve redirect. Se tiver acontencido um reddirect
        os próximos requests serao feitos nesse destino, até que aconteça um novo
        redirect
        Faremos após a resolução da issue: https://github.com/pnuckowski/aioresponses/issues/119
        """
        self.fail()

    async def test_mesos_client_try_all_mesos_master_urls_on_exception(self):
        """
        Se uma (ou mais) das URLs estiver com problemas, devemos tentar todas as outras antes de retornar uma exception
        """
        agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S0"
        agent_info = get_fixture(
            "agents/ead07ffb-5a61-42c9-9386-21b680597e6c-S0/info.json"
        )
        async with MesosClient(*settings.MESOS_API_URLS) as mesos:
            with aioresponses() as rsps:
                rsps.get(
                    f"{settings.MESOS_API_URLS[0]}/slaves?slave_id={agent_id}",
                    exception=Exception("Connection Error"),
                )
                rsps.get(
                    f"{settings.MESOS_API_URLS[1]}/slaves?slave_id={agent_id}",
                    status=200,
                    payload={"slaves": [agent_info], "recovered_slaves": []},
                )

                agent = await mesos.get_agent_by_id(agent_id=agent_id)
                self.assertEqual(agent_id, agent.id)

    async def test_mesos_client_raise_exception_if_all_urls_fail(self):
        """
        Lançamos exceção de não conseguirmos falar com nenhum mesos
        """

        mesos_urls = [settings.MESOS_API_URLS[0]]
        async with MesosClient(*mesos_urls) as mesos:
            with aioresponses() as rsps:
                rsps.get(
                    f"{mesos_urls[0]}/slaves?slave_id=id",
                    exception=Exception("Connection Error"),
                )
                with self.assertRaises(Exception):
                    await mesos.get_agent_by_id(agent_id="id")
