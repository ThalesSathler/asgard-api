from typing import List, Optional, Dict

from asgard.clients.apps.dtos.app_dto import AppDto
from asgard.clients.apps.dtos.app_stats_dto import AppStatsDto
from asgard.clients.apps.dtos.decision_dto import DecisionDto
from asgard.conf import settings
from asgard.http.client import http_client


async def get_all_apps() -> List[AppDto]:

    async with http_client as client:
        headers = {"Authorization": f"Token {settings.AUTOSCALER_AUTH_TOKEN}"}
        response = await client.get(
            f"{settings.ASGARD_API_ADDRESS}/v2/apps", headers=headers
        )
        all_apps_data = await response.json()

        app_dtos = [AppDto(**app_data) for app_data in all_apps_data["apps"]]
        return app_dtos


async def get_app_stats(app_id: str) -> Optional[AppStatsDto]:
    async with http_client as client:
        headers = {"Authorization": f"Token {settings.AUTOSCALER_AUTH_TOKEN}"}
        http_response = await client.get(
            f"{settings.ASGARD_API_ADDRESS}/apps/{app_id}/stats",
            headers=headers,
        )

        response = await http_response.json()

        app_stats_dto = AppStatsDto(**{"id": app_id, **response})

        return app_stats_dto


async def post_scaling_decisions(decisions: List[DecisionDto]) -> List[Dict]:
    post_body = list(map(DecisionDto.dict, decisions))

    async with http_client as client:
        await client.put(
            f"{settings.ASGARD_API_ADDRESS}/v2/apps",
            json=post_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {settings.AUTOSCALER_AUTH_TOKEN}",
            },
        )

    return list(post_body)
