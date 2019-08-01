from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from asgard.conf import settings
from asgard.http.client import http_client
from asgard.workers.models.app_stats import AppStats
from asgard.workers.models.scalable_app import ScalableApp
from asgard.workers.models.scaling_decision import Decision


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

        if "asgard.autoscale.ignore" in app.labels:
            if "all" in app.labels["asgard.autoscale.ignore"]:
                return False
            if "asgard.autoscale.cpu" in app.labels:
                if "cpu" not in app.labels["asgard.autoscale.ignore"]:
                    meets_criteria = True
            elif "asgard.autoscale.mem" in app.labels:
                if "mem" not in app.labels["asgard.autoscale.ignore"]:
                    meets_criteria = True
        else:
            if "asgard.autoscale.cpu" in app.labels:
                meets_criteria = True
            elif "asgard.autoscale.mem" in app.labels:
                meets_criteria = True

        return meets_criteria

    async def fetch_all_apps(self) -> List[ScalableApp]:
        async with http_client as client:
            response = await client.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps"
            )
            all_apps = await response.json()

            return [ScalableApp(**app) for app in all_apps]

    async def get_all_scalable_apps(self) -> List[ScalableApp]:
        all_apps = await self.fetch_all_apps()
        return list(filter(self.should_scale, all_apps))

    async def get_app_stats(self, app_id: int) -> Optional[AppStats]:
        async with http_client as client:
            http_response = await client.get(
                f"{settings.ASGARD_API_ADDRESS}/apps{app_id}/stats"
            )

            stats_json = await http_response.json()
            if stats_json:
                return AppStats(**{"id": app_id, **stats_json})

            return None

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
