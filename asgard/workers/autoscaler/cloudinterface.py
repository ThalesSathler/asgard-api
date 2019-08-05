from abc import ABC, abstractmethod
from typing import Dict, List

from asgard.conf import settings
from asgard.http.client import http_client
from asgard.workers.models.app_stats import AppStats
from asgard.workers.models.scalable_app import ScalableApp
from asgard.workers.models.scaling_decision import Decision
from asgard.workers.dtos.asgard_app import AppStatsDto, AppDto, AppConverter, AppStatsConverter


class CloudInterface(ABC):
    @abstractmethod
    def should_scale(self, app: ScalableApp) -> bool:
        pass

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
    def should_scale(self, app: ScalableApp) -> bool:
        meets_criteria = False

        if app.autoscale_ignore:
            if "all" in app.autoscale_ignore:
                return False
            if app.autoscale_cpu:
                if "cpu" not in app.autoscale_ignore:
                    meets_criteria = True
            elif app.autoscale_mem:
                if "mem" not in app.autoscale_ignore:
                    meets_criteria = True
        else:
            if app.autoscale_cpu:
                meets_criteria = True
            elif app.autoscale_mem:
                meets_criteria = True

        return meets_criteria

    async def fetch_all_apps(self) -> List[ScalableApp]:

        async with http_client as client:
            response = await client.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps"
            )
            all_apps_data = await response.json()

            if all_apps_data:
                app_dtos = [AppDto(**app_data) for app_data in all_apps_data]
                apps = AppConverter.all_to_model(app_dtos)
                return apps

            return list()

    async def get_all_scalable_apps(self) -> List[ScalableApp]:
        all_apps = await self.fetch_all_apps()
        if all_apps:
            return list(filter(self.should_scale, all_apps))

        return list()

    async def get_app_stats(self, app_id: str) -> AppStats:
        async with http_client as client:
            http_response = await client.get(
                f"{settings.ASGARD_API_ADDRESS}/apps/{app_id}/stats"
            )

            response = await http_response.json()

            if len(response["stats"]["errors"]) > 0:
                return None

            app_stats_dto = AppStatsDto(**{"id": app_id, **response})

            return AppStatsConverter.to_model(app_stats_dto)

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
