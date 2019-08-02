from aioresponses import aioresponses
from asynctest import TestCase, mock

from asgard.backends.marathon.impl import MarathonAppsBackend
from asgard.backends.mesos.impl import MesosOrchestrator, MesosAgentsBackend
from asgard.conf import settings
from asgard.models.account import Account
from asgard.models.user import User
from hollowman import log
from itests.util import USER_WITH_MULTIPLE_ACCOUNTS_DICT, ACCOUNT_DEV_DICT
from tests.conf import TEST_LOCAL_AIOHTTP_ADDRESS
from tests.utils import ClusterOptions, build_mesos_cluster, get_fixture


class MesosOrchestratorTest(TestCase):
    async def setUp(self):
        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        self.account = Account(**ACCOUNT_DEV_DICT)
        self.account.owner = "asgard"

        self.account_dev = Account(**ACCOUNT_DEV_DICT)

        self.mesos_backend = MesosOrchestrator(
            MesosAgentsBackend(), MarathonAppsBackend()
        )

    async def test_get_agents_filtered_by_namespace(self):
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(
                rsps,
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S10",
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S11",
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S12",
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S9",
            )

            agents = await self.mesos_backend.get_agents(
                self.user, self.account
            )
            self.assertEqual(4, len(agents))
            self.assertEqual(
                set(["asgard"]),
                set([agent.attributes["owner"] for agent in agents]),
            )
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S10", agents[0].id
            )
            self.assertEqual(2, agents[0].total_apps)

            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S11", agents[1].id
            )
            self.assertEqual(0, agents[1].total_apps)

            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S12", agents[2].id
            )
            self.assertEqual(1, agents[2].total_apps)

            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S9", agents[3].id
            )
            self.assertEqual(1, agents[3].total_apps)

    async def test_get_agents_remove_unused_fields(self):
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(rsps, "ead07ffb-5a61-42c9-9386-21b680597e6c-S9")
            agents = await self.mesos_backend.get_agents(
                self.user, self.account
            )
            self.assertEqual(1, len(agents))
            self.assertEqual("asgard", agents[0].attributes["owner"])

    async def test_get_agent_by_id_includes_app_count_and_list(self):
        agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S10"
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(rsps, agent_id)
            agent = await self.mesos_backend.get_agent_by_id(
                agent_id, self.user, self.account
            )
            self.assertEqual(agent_id, agent.id)
            self.assertEqual(2, agent.total_apps)
            expected_app_ids = sorted(
                ["captura/wetl/visitcentral", "infra/asgard/api"]
            )
            self.assertEqual(
                expected_app_ids, sorted([app.id for app in agent.applications])
            )

    async def test_get_agent_by_id_includes_individual_usage_stats(self):
        agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S10"
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(rsps, agent_id)
            agent = await self.mesos_backend.get_agent_by_id(
                agent_id, self.user, self.account
            )
            self.assertEqual(agent_id, agent.id)
            self.assertEqual(
                {"cpu_pct": "16.00", "ram_pct": "22.50"}, agent.stats
            )

    async def test_get_agent_by_id_logs_error_if_failed(self):
        """
        O campo total_apps retorna com valor 0 caso não tenha sido possível obter a lista de apps rodando em um Agent.
        Nesse caso o campo `errors` deverá estar preenchido
        """
        agent_data = get_fixture(
            "agents/ead07ffb-5a61-42c9-9386-21b680597e6c-S10/info.json"
        )
        agent_id = agent_data["id"]
        agent_hostname = agent_data["hostname"]
        with aioresponses(
            passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]
        ) as rsps, mock.patch.object(log, "logger") as logger_mock:
            build_mesos_cluster(
                rsps, {"id": agent_id, "apps": ClusterOptions.CONNECTION_ERROR}
            )
            agent = await self.mesos_backend.get_agent_by_id(
                agent_id, self.user, self.account
            )
            self.assertEqual(agent_id, agent.id)
            self.assertEqual([], agent.applications)
            self.assertEqual(0, agent.total_apps)
            self.assertEqual({"total_apps": "INDISPONIVEL"}, agent.errors)
            logger_mock.exception.assert_called_with(
                {
                    "event": "Erro buscando agent applications",
                    "agent": agent_id,
                    "hostname": agent_hostname,
                }
            )

    async def test_get_agent_by_id_returns_None_for_agent_in_another_namespace(
        self
    ):
        slave_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S0"
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(rsps, slave_id)
            agent = await self.mesos_backend.get_agent_by_id(
                slave_id,  # Agent from asgard-infra namespace
                self.user,
                self.account,
            )
            self.assertIsNone(agent)

    async def test_get_agent_by_id_return_None_if_agent_not_found(self):
        slave_id = "39e1a8e3-0fd1-4ba6-981d-e01318944957-S2"
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            rsps.get(
                f"{settings.MESOS_API_URLS[0]}/redirect",
                status=301,
                headers={"Location": settings.MESOS_API_URLS[0]},
            )
            rsps.get(
                f"{settings.MESOS_API_URLS[0]}/slaves?slave_id={slave_id}",
                payload={"slaves": []},
                status=200,
            )
            agent = await self.mesos_backend.get_agent_by_id(
                slave_id,  # Agent from asgard-infra namespace
                self.user,
                self.account,
            )
            self.assertIsNone(agent)

    async def test_get_apps_returns_empty_list_if_agent_not_found(self):
        slave_id = "39e1a8e3-0fd1-4ba6-981d-e01318944957-S2"
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            rsps.get(
                f"{settings.MESOS_API_URLS[0]}/redirect",
                status=301,
                headers={"Location": settings.MESOS_API_URLS[0]},
            )
            rsps.get(
                f"{settings.MESOS_API_URLS[0]}/slaves?slave_id={slave_id}",
                payload={"slaves": []},
                status=200,
            )

            agent = await self.mesos_backend.get_agent_by_id(
                slave_id, self.user, self.account
            )
            apps = await self.mesos_backend.get_apps_running_for_agent(
                self.user, agent
            )
            self.assertEqual(0, len(apps))

    async def test_get_apps_returns_empty_list_if_no_apps_running_on_agent(
        self
    ):
        agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S4"
        slave = get_fixture(f"agents/{agent_id}/info.json")
        slave_id = slave["id"]
        self.account.owner = slave["attributes"]["owner"]
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(rsps, agent_id)
            agent = await self.mesos_backend.get_agent_by_id(
                slave_id, self.user, self.account
            )
            apps = await self.mesos_backend.get_apps_running_for_agent(
                self.user, agent
            )
            self.assertEqual(0, len(apps))

    async def test_get_apps_returns_apps_running_on_agent(self):
        agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S0"
        slave = get_fixture(f"agents/{agent_id}/info.json")
        slave_id = slave["id"]
        slave_owner = slave["attributes"]["owner"]
        self.account.owner = slave_owner

        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(rsps, agent_id)
            agent = await self.mesos_backend.get_agent_by_id(
                slave_id, self.user, self.account
            )
            apps = await self.mesos_backend.get_apps_running_for_agent(
                self.user, agent
            )
            self.assertEqual(5, len(apps))

            expected_app_ids = sorted(
                [
                    "captura/wetl/visitcentral",
                    "portal/api",
                    "captura/kirby/feeder",
                    "infra/asgard/api",
                    "infra/rabbitmq",
                ]
            )
            self.assertEqual(expected_app_ids, sorted([app.id for app in apps]))
