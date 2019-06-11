

class PeriodicStateChecker:
    def __init__(self, cloudinterface):
        self.cloud_interface = cloudinterface

    async def get_scalable_apps_stats(self):
        apps = await self.cloud_interface.get_all_scalable_apps()

        return map(lambda app: await self.cloud_interface.get_app_stats(app["id"]), apps)
