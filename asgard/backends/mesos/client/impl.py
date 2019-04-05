from typing import List, Tuple, Optional, Dict

from asgard.backends.mesos.models.agent import MesosAgent
from asgard.http.client import http_client


class MesosClient:
    def __init__(self, mesos_api_url: str, *aditional_api_urls) -> None:
        self.mesos_adresses = tuple([mesos_api_url]) + aditional_api_urls

    async def __aenter__(self, *args, **kwargs):
        return self

    async def __aexit__(self, *args, **kwargs):
        pass

    async def _json_response(self, path: str) -> Dict:
        for addr in self.mesos_adresses:
            try:
                async with http_client.get(
                    f"{addr}{path}", allow_redirects=True
                ) as response:
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
