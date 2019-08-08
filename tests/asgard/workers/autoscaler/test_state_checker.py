from aioresponses import aioresponses
from asynctest import TestCase

from asgard.conf import settings
from asgard.workers.autoscaler.cloudinterface import (
    AsgardInterface as AsgardCloudInterface,
)
from asgard.workers.autoscaler.periodicstatechecker import PeriodicStateChecker


class TestStateChecker(TestCase):
    async def test_get_scalable_apps_stats_no_scalable_apps(self):
        state_checker = PeriodicStateChecker(AsgardCloudInterface())
        with aioresponses() as rsps:
            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps", status=200, payload=[]
            )

            scalable_apps = await state_checker.get_scalable_apps_stats()

            self.assertEqual(0, len(scalable_apps))

    async def test_get_scalable_apps_stats_one_scalable_app(self):
        state_checker = PeriodicStateChecker(AsgardCloudInterface())
        with aioresponses() as rsps:

            apps_fixture = [
                {
                    "id": "test_app1",
                    "cpu": 3.5,
                    "mem": 1.0,
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                        "asgard.autoscale.ignore": "all",
                    },
                },
                {
                    "id": "/test_app2",
                    "cpu": 3.5,
                    "mem": 1.0,
                    "labels": {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1,
                        "asgard.autoscale.ignore": "",
                    },
                },
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=apps_fixture,
            )

            stats_fixture = {
                "stats": {
                    "type": "ASGARD",
                    "errors": {},
                    "cpu_pct": "1",
                    "ram_pct": "1",
                    "cpu_thr_pct": "1",
                }
            }

            for app in apps_fixture:
                rsps.get(
                    f'{settings.ASGARD_API_ADDRESS}/apps{app["id"]}/stats',
                    status=200,
                    payload=stats_fixture,
                )

            scalable_apps = await state_checker.get_scalable_apps_stats()

            self.assertEqual(1, len(scalable_apps))
