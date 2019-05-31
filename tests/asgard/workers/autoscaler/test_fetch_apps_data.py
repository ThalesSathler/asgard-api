from asynctest import TestCase
from asgard.workers.base import Autoscaler
from aioresponses import aioresponses
from asgard.conf import settings


class FetchAppsDataTest(TestCase):
    async def test_get_all_apps_data(self):
        scaler = Autoscaler()

        with aioresponses() as rsps:
            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=[
                    {"id": "test_app"},
                    {"id": "test_app2"},
                    {"id": "test_app3"},
                    {"id": "test_app4"},
                ],
            )
            apps = await scaler.fetch_all_apps()

        self.assertEqual(4, len(apps))
        self.assertEqual("test_app", apps[0]["id"])
        self.assertEqual("test_app2", apps[1]["id"])
        self.assertEqual("test_app3", apps[2]["id"])
        self.assertEqual("test_app4", apps[3]["id"])

    async def test_get_all_apps_data_no_data_found(self):
        scaler = Autoscaler()

        with aioresponses() as rsps:
            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps", status=200, payload=[]
            )

            apps = await scaler.fetch_all_apps()

        self.assertEqual([], apps)
