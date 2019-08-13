from typing import List

from asgard.workers.autoscaler.cloudinterface import CloudInterface
from asgard.workers.models.scalable_app import ScalableApp


class PeriodicStateChecker:
    def __init__(self, cloudinterface: CloudInterface) -> None:
        self.cloud_interface = cloudinterface

    async def get_scalable_apps_stats(self) -> List[ScalableApp]:
        apps = await self.cloud_interface.get_all_scalable_apps()

        if apps:
            for app in apps:
                app.app_stats = await self.cloud_interface.get_app_stats(app)

        return apps
