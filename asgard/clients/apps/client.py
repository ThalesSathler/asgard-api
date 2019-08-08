from typing import List, Optional, Dict

from asgard.clients.apps.dtos.app_dto import AppDto
from asgard.clients.apps.dtos.app_stats_dto import AppStatsDto
from asgard.clients.apps.dtos.decision_dto import DecisionDto
from asgard.conf import settings
from asgard.http.client import http_client


async def get_all_apps() -> List[AppDto]:

    async with http_client as client:
        response = await client.get(f"{settings.ASGARD_API_ADDRESS}/v2/apps")
        all_apps_data = await response.json()

        if all_apps_data:
            app_dtos = [AppDto(**app_data) for app_data in all_apps_data]
            return app_dtos

        return list()


async def get_app_stats(app_id: str) -> Optional[AppStatsDto]:
    async with http_client as client:
        http_response = await client.get(
            f"{settings.ASGARD_API_ADDRESS}/apps/{app_id}/stats"
        )

        response = await http_response.json()

        if len(response["stats"]["errors"]) > 0:
            return None

        app_stats_dto = AppStatsDto(**{"id": app_id, **response})

        return app_stats_dto


async def post_scaling_decisions(decisions: List[DecisionDto]) -> List[Dict]:
    post_body = list(map(DecisionDto.to_dict, decisions))

    async with http_client as client:
        await client.put(
            f"{settings.ASGARD_API_ADDRESS}/v2/apps",
            json=post_body,
            headers={"Content-Type": "application/json"},
        )

    return list(post_body)
