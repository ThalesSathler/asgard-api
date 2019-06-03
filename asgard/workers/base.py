from asgard.http.client import http_client
from asgard.conf import settings


class Autoscaler:
    def should_scale(self, labels):
        meets_criteria = False

        if "asgard.autoscale.ignore" in labels:
            ignores = labels["asgard.autoscale.ignore"]
        else:
            ignores = ""

        if "all" in ignores:
            return False

        if "asgard.autoscale.cpu" in labels:
            if "cpu" not in ignores:
                meets_criteria = True
        elif "asgard.autoscale.mem" in labels:
            if "mem" not in ignores:
                meets_criteria = True

        return meets_criteria

    async def fetch_all_apps(self):
        async with http_client as client:
            response = await client.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps"
            )
            return await response.json()

    async def get_all_scalable_apps(self):
        def app_filter (app):
            if 'labels' in app:
                return self.should_scale(app['labels'])
            return False

        all_apps = await self.fetch_all_apps()
        return list(filter(app_filter, all_apps))
