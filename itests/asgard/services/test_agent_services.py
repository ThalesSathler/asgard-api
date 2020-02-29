from aioresponses import aioresponses
from tests.utils import build_mesos_cluster

from asgard.api.apps import app
from asgard.backends.marathon.impl import MarathonAppsBackend
from asgard.backends.mesos.impl import MesosAgentsBackend, MesosOrchestrator
from asgard.models.account import Account
from asgard.models.user import User
from asgard.services.agents import AgentsService
from asyncworker.testing import HttpClientContext
from itests.util import (
    BaseTestCase,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    ACCOUNT_DEV_DICT,
)


class AgentsServiceTest(BaseTestCase):
    async def setUp(self):
        await super(AgentsServiceTest, self).setUp()
        self.mesos_orchestrator = MesosOrchestrator(
            agents_backend=MesosAgentsBackend(),
            apps_backend=MarathonAppsBackend(),
        )
        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        self.account = Account(**ACCOUNT_DEV_DICT)
        self.agents_service = AgentsService()

    async def tearDown(self):
        await super(AgentsServiceTest, self).tearDown()

    async def test_get_apps_running_for_agent_mesos_orchestrator_zero_apps(
        self
    ):
        async with HttpClientContext(app) as client:
            local_address = (
                f"http://{client._server.host}:{client._server.port}"
            )
            with aioresponses(passthrough=[local_address]) as rsps:
                agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S44"
                build_mesos_cluster(rsps, agent_id)
                agent = await self.agents_service.get_agent_by_id(
                    agent_id, self.user, self.account, self.mesos_orchestrator
                )
                apps = await self.agents_service.get_apps_running_for_agent(
                    self.user, agent, self.mesos_orchestrator
                )
                self.assertEquals([], apps)

    async def test_get_apps_running_for_agent_mesos_orchestrator_some_apps(
        self
    ):
        async with HttpClientContext(app) as client:
            local_address = (
                f"http://{client._server.host}:{client._server.port}"
            )
            with aioresponses(passthrough=[local_address]) as rsps:
                agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S9"
                build_mesos_cluster(rsps, agent_id)
                self.account.owner = "asgard"
                agent = await self.agents_service.get_agent_by_id(
                    agent_id, self.user, self.account, self.mesos_orchestrator
                )
                apps = await self.agents_service.get_apps_running_for_agent(
                    self.user, agent, self.mesos_orchestrator
                )
                self.assertEquals(1, len(apps))
