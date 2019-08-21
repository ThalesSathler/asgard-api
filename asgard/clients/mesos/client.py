from typing import List, Optional, Dict

from asgard.clients.mesos.models.agent import MesosAgent
from asgard.http.client import HttpClient


class MesosClient:
    def __init__(self, mesos_api_url: str, *aditional_api_urls) -> None:
        self.mesos_adresses = tuple([mesos_api_url]) + aditional_api_urls
        self.http_client = HttpClient()

    async def __aenter__(self, *args, **kwargs):
        return self

    async def __aexit__(self, *args, **kwargs):
        pass

    async def _json_response(self, path: str) -> Dict:
        for addr in self.mesos_adresses:
            try:
                response = await self.http_client.get(f"{addr}{path}")
                return await response.json()
            except Exception:
                pass
        raise Exception(f"No more servers to try: {self.mesos_adresses}")

    async def get_agent_by_id(self, agent_id: str) -> Optional[MesosAgent]:
        data = await self._json_response(f"/slaves?slave_id={agent_id}")
        if data["slaves"]:
            agent = MesosAgent(**data["slaves"][0])
            return agent

        return None

    async def get_agents(self) -> List[MesosAgent]:
        data = await self._json_response(f"/slaves")
        if "slaves" in data:
            agents = [MesosAgent(**agent_info) for agent_info in data["slaves"]]
            return agents
        return []
