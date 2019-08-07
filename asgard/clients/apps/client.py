from typing import List, Optional, Dict

from asgard.http.client import http_client
from asgard.clients.apps.dtos.app_dto import AppDto
from asgard.clients.apps.dtos.app_stats_dto import AppStatsDto
from asgard.conf import settings


async def get_all_apps() -> List[AppDto]:

    async with http_client as client:
        response = await client.get(
            f"{settings.ASGARD_API_ADDRESS}/v2/apps"
        )
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