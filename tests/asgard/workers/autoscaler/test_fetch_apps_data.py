from aioresponses import aioresponses
from asynctest import TestCase
from yarl import URL

from asgard.conf import settings
from asgard.workers.autoscaler.asgard_cloudinterface import AsgardInterface
from asgard.workers.models.app_stats import AppStats
from asgard.workers.models.scalable_app import ScalableApp


class TestFetchAppsData(TestCase):
    async def test_get_all_apps_data(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={
                    "apps": [
                        {
                            "id": "/test_app",
                            "cpus": "0.1",
                            "mem": "0.2",
                            "labels": {},
                        },
                        {
                            "id": "/test_app2",
                            "cpus": "0.1",
                            "mem": "0.2",
                            "labels": {},
                        },
                        {
                            "id": "/test_app3",
                            "cpus": "0.1",
                            "mem": "0.2",
                            "labels": {},
                        },
                        {
                            "id": "/test_app4",
                            "cpus": "0.1",
                            "mem": "0.2",
                            "labels": {},
                        },
                    ]
                },
            )
            apps = await scaler.fetch_all_apps()

        fixture = [
            ScalableApp("test_app"),
            ScalableApp("test_app2"),
            ScalableApp("test_app3"),
            ScalableApp("test_app4"),
        ]

        self.assertEqual(len(fixture), len(apps))

        for i in range(len(fixture)):
            self.assertEqual(fixture[i].id, apps[i].id)

    async def test_get_all_apps_data_no_data_found(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"apps": []},
            )

            apps = await scaler.fetch_all_apps()

        self.assertEqual([], apps)

    async def test_get_all_apps_which_should_be_scaled_all_apps_should(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            payload = {
                "apps": [
                    {
                        "id": "/test_app1",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.3,
                            "asgard.autoscale.mem": 0.8,
                        },
                    },
                    {
                        "id": "/test_app2",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.1,
                            "asgard.autoscale.mem": 0.1,
                        },
                    },
                    {
                        "id": "/test_app3",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.5,
                            "asgard.autoscale.mem": 0.7,
                        },
                    },
                ]
            }

            fixture = [
                ScalableApp("test_app1", cpu_threshold=0.3, mem_threshold=0.8),
                ScalableApp("test_app2", cpu_threshold=0.1, mem_threshold=0.1),
                ScalableApp("test_app3", cpu_threshold=0.5, mem_threshold=0.7),
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
                self.assertEqual(
                    fixture[i].cpu_threshold, apps[i].cpu_threshold
                )
                self.assertEqual(
                    fixture[i].mem_threshold, apps[i].mem_threshold
                )

    async def test_get_all_apps_which_should_be_scaled_no_app_should(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            fixture = {
                "apps": [
                    {
                        "id": "/test_app1",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.3,
                            "asgard.autoscale.mem": 0.8,
                            "asgard.autoscale.ignore": "all",
                        },
                    },
                    {
                        "id": "/test_app2",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.1,
                            "asgard.autoscale.mem": 0.1,
                            "asgard.autoscale.ignore": "cpu;mem",
                        },
                    },
                    {
                        "id": "/test_app3",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.5,
                            "asgard.autoscale.ignore": "cpu",
                        },
                    },
                ]
            }

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
            payload = {
                "apps": [
                    {
                        "id": "/test_app1",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.3,
                            "asgard.autoscale.mem": 0.8,
                            "asgard.autoscale.ignore": "all",
                        },
                    },
                    {
                        "id": "/test_app2",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.1,
                            "asgard.autoscale.mem": 0.1,
                        },
                    },
                    {
                        "id": "/test_app3",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.5,
                            "asgard.autoscale.ignore": "cpu",
                        },
                    },
                ]
            }

            fixture = [
                ScalableApp(
                    "test_app1", cpu_threshold=None, mem_threshold=None
                ),
                ScalableApp("test_app2", cpu_threshold=0.1, mem_threshold=0.1),
                ScalableApp(
                    "test_app3", cpu_threshold=None, mem_threshold=None
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
            self.assertEqual(fixture[1].cpu_threshold, apps[0].cpu_threshold)
            self.assertEqual(fixture[1].mem_threshold, apps[0].mem_threshold)

    async def test_get_all_apps_which_should_be_scaled_one_app_should_not(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            payload = {
                "apps": [
                    {
                        "id": "/test_app1",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.3,
                            "asgard.autoscale.mem": 0.8,
                        },
                    },
                    {
                        "id": "/test_app2",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.1,
                            "asgard.autoscale.mem": 0.1,
                        },
                    },
                    {
                        "id": "/test_app3",
                        "cpus": "0.2",
                        "mem": "0.2",
                        "labels": {
                            "asgard.autoscale.cpu": 0.5,
                            "asgard.autoscale.ignore": "cpu",
                        },
                    },
                ]
            }

            fixture = [
                ScalableApp("test_app1", cpu_threshold=0.3, mem_threshold=0.8),
                ScalableApp("test_app2", cpu_threshold=0.1, mem_threshold=0.1),
                ScalableApp(
                    "test_app3", cpu_threshold=None, mem_threshold=None
                ),
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=payload,
            )

            apps = await scaler.get_all_scalable_apps()

            self.assertEqual(2, len(apps))

            self.assertEqual(fixture[0].id, apps[0].id)
            self.assertEqual(fixture[0].cpu_threshold, apps[0].cpu_threshold)
            self.assertEqual(fixture[0].mem_threshold, apps[0].mem_threshold)

            self.assertEqual(fixture[1].id, apps[1].id)
            self.assertEqual(fixture[1].cpu_threshold, apps[1].cpu_threshold)
            self.assertEqual(fixture[1].mem_threshold, apps[1].mem_threshold)

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
            app = ScalableApp("app_test1")

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/apps/{app.id}/stats/avg-1min",
                status=200,
                payload=payload,
            )

            fixture = AppStats(cpu_usage=0.93, mem_usage=8.91)

            app_stats = await scaler.get_app_stats(app)

            self.assertEqual(fixture.cpu_usage, app_stats.cpu_usage)
            self.assertEqual(fixture.mem_usage, app_stats.mem_usage)

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
            app = ScalableApp("app_test1")

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/apps/{app.id}/stats/avg-1min",
                status=200,
                payload=fixture,
            )

            stats = await scaler.get_app_stats(app)

            self.assertEqual(None, stats)
            self.assertEqual(None, app.app_stats)

    # async def test_sending_auth_in_headers(self):
    #     scaler = AsgardInterface()
    #
    #     with aioresponses() as rsps:
    #         payload = {
    #             "stats": {
    #                 "type": "ASGARD",
    #                 "errors": {},
    #                 "cpu_pct": "0.93",
    #                 "ram_pct": "8.91",
    #                 "cpu_thr_pct": "0.06",
    #             }
    #         }
    #         app = ScalableApp("app_test1")
    #
    #         headers_fixture = {
    #             "Authorization": f"Token {settings.AUTOSCALER_AUTH_TOKEN}"
    #         }
    #
    #         rsps.get(
    #             f"{settings.ASGARD_API_ADDRESS}/apps/{app.id}/stats/avg-1min",
    #             status=200,
    #             payload=payload,
    #         )
    #
    #         app_with_stats = await scaler.get_app_stats(app)
    #
    #         calls = rsps.requests.get(
    #             (
    #                 "GET",
    #                 URL(
    #                     f"{settings.ASGARD_API_ADDRESS}/apps/{app.id}/stats/avg-1min"
    #                 ),
    #             )
    #         )
    #
    #         self.assertIsNotNone(calls)
    #         self.assertEqual(headers_fixture, calls[0].kwargs.get("headers"))
