from asgard.workers.autoscaler.cloudinterface import CloudInterface


class PeriodicStateChecker:
    def __init__(self, cloudinterface: CloudInterface) -> None:
        self.cloud_interface = cloudinterface

    async def get_scalable_apps_stats(self):
        apps = await self.cloud_interface.get_all_scalable_apps()

        resp = []
        for app in apps:
            app_stats = await self.cloud_interface.get_app_stats(app["id"])
            app_dict = dict()
            app_dict[app["id"]] = app_stats
            resp.append(app_dict)

        return resp
