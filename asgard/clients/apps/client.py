from typing import List, Optional, Dict

from asgard.clients.apps.dtos.app_dto import AppDto
from asgard.clients.apps.dtos.app_stats_dto import AppStatsDto
from asgard.clients.apps.dtos.decision_dto import DecisionDto
from asgard.conf import settings
from asgard.http.client import HttpClient


class AppsClient:
    def __init__(self):
        self._http_client = HttpClient(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {settings.AUTOSCALER_AUTH_TOKEN}",
            }
        )

    async def get_all_apps(self) -> List[AppDto]:
        response = await self._http_client.get(
            url=f"{settings.ASGARD_API_ADDRESS}/v2/apps"
        )
        all_apps_data = await response.json()

        app_dtos = [AppDto(**app_data) for app_data in all_apps_data["apps"]]
        return app_dtos

    async def get_app_stats(self, app_id: str) -> Optional[AppStatsDto]:
        response = await self._http_client.get(
            url=f"{settings.ASGARD_API_ADDRESS}/apps/{app_id}/stats/avg-1min"
        )

        app_stats_data = await response.json()

        app_stats_dto = AppStatsDto(**{"id": app_id, **app_stats_data})

        return app_stats_dto

    async def post_scaling_decisions(
        self, decisions: List[DecisionDto]
    ) -> List[Dict]:
        post_body = list(map(DecisionDto.dict, decisions))

        await self._http_client.put(
            url=f"{settings.ASGARD_API_ADDRESS}/v2/apps", json=post_body
        )

        return list(post_body)
