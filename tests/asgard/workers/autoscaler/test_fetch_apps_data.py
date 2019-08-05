from aioresponses import aioresponses
from asynctest import TestCase

from asgard.conf import settings
from asgard.workers.autoscaler.cloudinterface import AsgardInterface
from asgard.workers.models.app_stats import AppStats
from asgard.workers.models.scalable_app import ScalableApp


class TestFetchAppsData(TestCase):
    async def test_get_all_apps_data(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=[
                    {
                        "id": "/test_app",
                        "cpu": "0.1",
                        "mem": "0.2",
                        "labels": {}
                    },
                    {
                        "id": "/test_app2",
                        "cpu": "0.1",
                        "mem": "0.2",
                        "labels": {}
                    },
                    {
                        "id": "/test_app3",
                        "cpu": "0.1",
                        "mem": "0.2",
                        "labels": {}
                    },
                    {
                        "id": "/test_app4",
                        "cpu": "0.1",
                        "mem": "0.2",
                        "labels": {}
                    },
                ],
            )
            apps = await scaler.fetch_all_apps()

        fixture = [
            ScalableApp('test_app'),
            ScalableApp('test_app2'),
            ScalableApp('test_app3'),
            ScalableApp('test_app4')
        ]

        self.assertEqual(len(fixture), len(apps))

        for i in range(len(fixture)):
            self.assertEqual(fixture[i].id, apps[i].id)

    async def test_get_all_apps_data_no_data_found(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps", status=200, payload=[]
            )

            apps = await scaler.fetch_all_apps()

        self.assertEqual([], apps)

    async def test_get_all_apps_which_should_be_scaled_all_apps_should(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            payload = [
                {
                    "id": "/test_app1",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                    },
                },
                {
                    "id": "/test_app2",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1,
                    },
                },
                {
                    "id": "/test_app3",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.5,
                        "asgard.autoscale.mem": 0.7,
                    },
                },
            ]

            fixture = [
                ScalableApp("test_app1", autoscale_cpu=0.3, autoscale_mem=0.8),
                ScalableApp("test_app2", autoscale_cpu=0.1, autoscale_mem=0.1),
                ScalableApp("test_app3", autoscale_cpu=0.5, autoscale_mem=0.7),
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=payload,
            )

            apps = await scaler.get_all_scalable_apps()

            self.assertEqual(len(fixture), len(apps))

            for i in range(len(fixture)):
                self.assertEqual(fixture[i].id, apps[i].id)
                self.assertEqual(fixture[i].autoscale_cpu, apps[i].autoscale_cpu)
                self.assertEqual(fixture[i].autoscale_mem, apps[i].autoscale_mem)

    async def test_get_all_apps_which_should_be_scaled_no_app_should(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            fixture = [
                {
                    "id": "/test_app1",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                        "asgard.autoscale.ignore": "all",
                    },
                },
                {
                    "id": "/test_app2",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1,
                        "asgard.autoscale.ignore": "cpu;mem",
                    },
                },
                {
                    "id": "/test_app3",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.5,
                        "asgard.autoscale.ignore": "cpu",
                    },
                },
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=fixture,
            )

            apps = await scaler.get_all_scalable_apps()

            self.assertEqual([], apps)
            self.assertEqual(0, len(apps))

    async def test_get_all_apps_which_should_be_scaled_one_app_should(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            payload = [
                {
                    "id": "/test_app1",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                        "asgard.autoscale.ignore": "all",
                    },
                },
                {
                    "id": "/test_app2",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1,
                    },
                },
                {
                    "id": "/test_app3",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.5,
                        "asgard.autoscale.ignore": "cpu",
                    },
                },
            ]

            fixture = [
                ScalableApp(
                    "test_app1",
                    autoscale_cpu=None,
                    autoscale_mem=None,
                ),
                ScalableApp(
                    "test_app2",
                    autoscale_cpu=0.1,
                    autoscale_mem=0.1
                ),
                ScalableApp(
                    "test_app3",
                    autoscale_cpu=None,
                    autoscale_mem=None
                ),
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=payload,
            )

            apps = await scaler.get_all_scalable_apps()

            self.assertEqual(1, len(apps))

            self.assertEqual(fixture[1].id, apps[0].id)
            self.assertEqual(fixture[1].autoscale_cpu, apps[0].autoscale_cpu)
            self.assertEqual(fixture[1].autoscale_mem, apps[0].autoscale_mem)

    async def test_get_all_apps_which_should_be_scaled_one_app_should_not(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            payload = [
                {
                    "id": "/test_app1",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                    },
                },
                {
                    "id": "/test_app2",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1,
                    },
                },
                {
                    "id": "/test_app3",
                    "cpu": "0.2",
                    "mem": "0.2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.5,
                        "asgard.autoscale.ignore": "cpu",
                    },
                },
            ]

            fixture = [
                ScalableApp("test_app1", autoscale_cpu=0.3, autoscale_mem=0.8),
                ScalableApp("test_app2", autoscale_cpu=0.1, autoscale_mem=0.1),
                ScalableApp("test_app3", autoscale_cpu=None, autoscale_mem=None),
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=payload,
            )

            apps = await scaler.get_all_scalable_apps()

            self.assertEqual(2, len(apps))

            self.assertEqual(fixture[0].id, apps[0].id)
            self.assertEqual(fixture[0].autoscale_cpu, apps[0].autoscale_cpu)
            self.assertEqual(fixture[0].autoscale_mem, apps[0].autoscale_mem)

            self.assertEqual(fixture[1].id, apps[1].id)
            self.assertEqual(fixture[1].autoscale_cpu, apps[1].autoscale_cpu)
            self.assertEqual(fixture[1].autoscale_mem, apps[1].autoscale_mem)

    async def test_get_app_stats_existing_app_id(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            payload = {
                "stats": {
                    "type": "ASGARD",
                    "errors": {},
                    "cpu_pct": "0.93",
                    "ram_pct": "8.91",
                    "cpu_thr_pct": "0.06",
                }
            }
            app_id = "app_test1"

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/apps/{app_id}/stats",
                status=200,
                payload=payload,
            )

            fixture = AppStats(app_id, cpu_usage=0.93, ram_usage=8.91)

            stats = await scaler.get_app_stats(app_id)

            self.assertEqual(fixture.id, stats.id)
            self.assertEqual(fixture.cpu_usage, stats.cpu_usage)
            self.assertEqual(fixture.ram_usage, stats.ram_usage)

    async def test_get_app_stats_non_existing_app_id(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            fixture = {
                "stats": {
                    "type": "ASGARD",
                    "errors": {},
                    "cpu_pct": "0",
                    "ram_pct": "0",
                    "cpu_thr_pct": "0",
                }
            }
            app_id = "app_test1"

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/apps/{app_id}/stats",
                status=200,
                payload=fixture,
            )

            stats = await scaler.get_app_stats(app_id)

            self.assertEqual(None, stats)
