from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from asgard.conf import settings
from asgard.http.client import http_client
from asgard.workers.models.app_stats import AppStats
from asgard.workers.models.scalable_app import ScalableApp
from asgard.workers.models.scaling_decision import Decision
from asgard.workers.converters.asgard_converter import AppStatsDto, AppDto, AppConverter, AppStatsConverter
import asgard.clients.apps.client as asgard_client


class CloudInterface(ABC):

    @abstractmethod
    async def fetch_all_apps(self) -> List[ScalableApp]:
        pass

    @abstractmethod
    async def get_all_scalable_apps(self) -> List[ScalableApp]:
        pass

    @abstractmethod
    async def get_app_stats(self, app_id) -> AppStats:
        pass

    @abstractmethod
    async def apply_decisions(self, scaling_decisions: Decision) -> List[Decision]:
        pass


class AsgardInterface(CloudInterface):

    async def fetch_all_apps(self) -> List[ScalableApp]:
        app_dtos = await asgard_client.get_all_apps()
        apps = AppConverter.all_to_model(app_dtos)

        return apps

    async def get_all_scalable_apps(self) -> List[ScalableApp]:
        all_apps = await self.fetch_all_apps()
        if all_apps:
            return list(filter(ScalableApp.is_set_to_scale, all_apps))

        return list()

    async def get_app_stats(self, app: ScalableApp) -> ScalableApp:
        app_stats_dto = await asgard_client.get_app_stats(app.id)
        app.app_stats = AppStatsConverter.to_model(app_stats_dto)

        return app

    async def apply_decisions(self, scaling_decisions: List[Decision]) -> List[Dict]:
        post_body = []

        for decision in scaling_decisions:
            app_scaling_json = {
                "id": decision.id
            }

            if decision.cpu is not None:
                app_scaling_json["cpus"] = decision.cpu
            if decision.mem is not None:
                app_scaling_json["mem"] = decision.mem

            post_body.append(app_scaling_json)

        async with http_client as client:
            http_response = await client.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                json=post_body
            )

        return post_body
