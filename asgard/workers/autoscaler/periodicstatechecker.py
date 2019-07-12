from typing import List

from asgard.workers.autoscaler.cloudinterface import CloudInterface
from asgard.workers.models.app_stats import AppStats


class PeriodicStateChecker:
    def __init__(self, cloudinterface: CloudInterface) -> None:
        self.cloud_interface = cloudinterface

    async def get_scalable_apps_stats(self) -> List[AppStats]:
        apps = await self.cloud_interface.get_all_scalable_apps()

        resp = []
        for app in apps:
            app_stats = await self.cloud_interface.get_app_stats(app.id)
            resp.append(app_stats)

        return resp
