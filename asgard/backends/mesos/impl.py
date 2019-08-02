from typing import List, Optional

from asgard.backends.base import Orchestrator, AgentsBackend
from asgard.backends.mesos.client.impl import MesosClient
from asgard.backends.mesos.models.agent import MesosAgent
from asgard.backends.mesos.models.app import MesosApp
from asgard.conf import settings
from asgard.models.account import Account
from asgard.models.agent import Agent
from asgard.models.app import App, AppStats
from asgard.models.user import User
from hollowman import log


async def populate_apps(agent: MesosAgent):
    try:
        agent.applications = await agent.apps()
        agent.total_apps = len(agent.applications)
    except Exception as e:
        agent.add_error(field_name="total_apps", error_msg="INDISPONIVEL")
        log.logger.exception(
            {
                "event": "Erro buscando agent applications",
                "agent": agent.id,
                "hostname": agent.hostname,
            }
        )


class MesosAgentsBackend(AgentsBackend):
    async def get_agents(
        self, user: User, account: Account
    ) -> List[MesosAgent]:
        async with MesosClient(*settings.MESOS_API_URLS) as mesos:
            filtered_agents: List[MesosAgent] = []
            client_agents = await mesos.get_agents()
            for client_agent in client_agents:
                agent = client_agent.to_asgard_model(MesosAgent)
                if not agent.attr_has_value("owner", account.owner):
                    continue
                await populate_apps(agent)
                await agent.calculate_stats()
                filtered_agents.append(agent)
        return filtered_agents

    async def get_by_id(
        self, agent_id: str, user: User, account: Account
    ) -> Optional[MesosAgent]:
        async with MesosClient(*settings.MESOS_API_URLS) as mesos:
            client_agent = await mesos.get_agent_by_id(agent_id=agent_id)
            if client_agent:
                agent = client_agent.to_asgard_model(MesosAgent)

                if agent.attr_has_value("owner", account.owner):
                    await populate_apps(agent)
                    await agent.calculate_stats()
                    return agent
        return None

    async def get_apps_running(self, user: User, agent: Agent) -> List[App]:
        if agent:
            return agent.applications
        return []


class MesosOrchestrator(Orchestrator):
    async def get_agents(
        self, user: User, account: Account
    ) -> List[MesosAgent]:
        return await self.agents_backend.get_agents(user, account)

    async def get_agent_by_id(
        self, agent_id: str, user: User, account: Account
    ) -> Optional[MesosAgent]:
        return await self.agents_backend.get_by_id(agent_id, user, account)

    async def get_apps_running_for_agent(
        self, user: User, agent: Agent
    ) -> List[MesosApp]:
        return await self.agents_backend.get_apps_running(user, agent)

    async def get_app_stats(
        self, app: App, user: User, account: Account
    ) -> AppStats:
        return await self.apps_backend.get_app_stats(app, user, account)
