from aioresponses import aioresponses
from asynctest import TestCase
from yarl import URL

from asgard.conf import settings
from asgard.workers.autoscaler.asgard_cloudinterface import (
    AsgardInterface as AsgardCloudInterface,
)
from asgard.workers.autoscaler.periodicstatechecker import PeriodicStateChecker
from asgard.workers.autoscaler.simple_decision_component import (
    DecisionComponent,
)


class AutoscalerTest(TestCase):
    async def test_scale_one_app(self):
        cloud_interface = AsgardCloudInterface()
        state_checker = PeriodicStateChecker(cloud_interface)
        decision_maker = DecisionComponent()

        with aioresponses() as rsps:
            stats_fixture = {
                "stats": {
                    "type": "ASGARD",
                    "errors": {},
                    "cpu_pct": "1",
                    "ram_pct": "1",
                    "cpu_thr_pct": "0",
                }
            }

            apps_fixture = [
                {
                    "id": "/test_app1",
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

            for app in apps_fixture:
                rsps.get(
                    f"{settings.ASGARD_API_ADDRESS}/apps{app['id']}/stats",
                    status=200,
                    payload=stats_fixture,
                )

            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test", "version": "1.0"},
            )

            apps_stats = await state_checker.get_scalable_apps_stats()
            scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
            await cloud_interface.apply_decisions(scaling_decision)

            scale_spy = rsps.requests.get(
                ("PUT", URL(f"{settings.ASGARD_API_ADDRESS}/v2/apps"))
            )

        self.assertEqual(1, len(scaling_decision))
        self.assertEqual(10, scaling_decision[0].mem)
        self.assertEqual(35, scaling_decision[0].cpu)
        self.assertIsNotNone(scale_spy)

    async def test_decide_to_scale_all_apps(self):
        cloud_interface = AsgardCloudInterface()
        state_checker = PeriodicStateChecker(cloud_interface)
        decision_maker = DecisionComponent()

        with aioresponses() as rsps:
            stats_fixture = {
                "stats": {
                    "type": "ASGARD",
                    "errors": {},
                    "cpu_pct": "1",
                    "ram_pct": "1",
                    "cpu_thr_pct": "0",
                }
            }

            apps_fixture = [
                {
                    "id": "/test_app1",
                    "cpu": 3.5,
                    "mem": 1.0,
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                        "asgard.autoscale.ignore": "cpu",
                    },
                },
                {
                    "id": "/test_app2",
                    "cpu": 3.5,
                    "mem": 1.0,
                    "labels": {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.6,
                        "asgard.autoscale.ignore": "mem",
                    },
                },
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=apps_fixture,
            )

            for app in apps_fixture:
                rsps.get(
                    f"{settings.ASGARD_API_ADDRESS}/apps{app['id']}/stats",
                    status=200,
                    payload=stats_fixture,
                )

            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test", "version": "1.0"},
            )

            apps_stats = await state_checker.get_scalable_apps_stats()
            scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
            await cloud_interface.apply_decisions(scaling_decision)

            scale_spy = rsps.requests.get(
                ("PUT", URL(f"{settings.ASGARD_API_ADDRESS}/v2/apps"))
            )

        self.assertEqual(len(apps_stats), len(scaling_decision))
        self.assertEqual(1.25, scaling_decision[0].mem)
        self.assertEqual(None, scaling_decision[0].cpu)
        self.assertEqual(None, scaling_decision[1].mem)
        self.assertEqual(35, scaling_decision[1].cpu)
        self.assertIsNotNone(scale_spy)

    async def test_decide_to_scale_some_apps(self):
        cloud_interface = AsgardCloudInterface()
        state_checker = PeriodicStateChecker(cloud_interface)
        decision_maker = DecisionComponent()

        with aioresponses() as rsps:
            stats_fixture = {
                "stats": {
                    "type": "ASGARD",
                    "errors": {},
                    "cpu_pct": "1",
                    "ram_pct": "1",
                    "cpu_thr_pct": "0",
                }
            }

            apps_fixture = [
                {
                    "id": "/test_app1",
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
                {
                    "id": "/test_app3",
                    "cpu": 3.5,
                    "mem": 1.0,
                    "labels": {
                        "asgard.autoscale.cpu": 0.5,
                        "asgard.autoscale.mem": 0.7,
                        "asgard.autoscale.ignore": "mem",
                    },
                },
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=apps_fixture,
            )

            for app in apps_fixture:
                rsps.get(
                    f"{settings.ASGARD_API_ADDRESS}/apps{app['id']}/stats",
                    status=200,
                    payload=stats_fixture,
                )

            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test", "version": "1.0"},
            )

            apps_stats = await state_checker.get_scalable_apps_stats()
            scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
            await cloud_interface.apply_decisions(scaling_decision)

            scale_spy = rsps.requests.get(
                ("PUT", URL(f"{settings.ASGARD_API_ADDRESS}/v2/apps"))
            )

        self.assertEqual(2, len(scaling_decision))
        self.assertEqual(10, scaling_decision[0].mem)
        self.assertEqual(35, scaling_decision[0].cpu)
        self.assertEqual(None, scaling_decision[1].mem)
        self.assertEqual(7, scaling_decision[1].cpu)
        self.assertIsNotNone(scale_spy)

    async def test_decide_to_scale_no_apps(self):
        cloud_interface = AsgardCloudInterface()
        state_checker = PeriodicStateChecker(cloud_interface)
        decision_maker = DecisionComponent()

        with aioresponses() as rsps:
            stats_fixture = {
                "stats": {
                    "type": "ASGARD",
                    "errors": {},
                    "cpu_pct": "1",
                    "ram_pct": "1",
                    "cpu_thr_pct": "0",
                }
            }

            apps_fixture = [
                {
                    "id": "/test_app1",
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
                        "asgard.autoscale.ignore": "cpu,mem",
                    },
                },
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=apps_fixture,
            )

            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test", "version": "1.0"},
            )

            for app in apps_fixture:
                rsps.get(
                    f"{settings.ASGARD_API_ADDRESS}/apps{app['id']}/stats",
                    status=200,
                    payload=stats_fixture,
                )

            apps = await state_checker.get_scalable_apps_stats()
            scaling_decision = decision_maker.decide_scaling_actions(apps)
            await cloud_interface.apply_decisions(scaling_decision)
            scale_spy = rsps.requests.get(
                ("PUT", URL(f"{settings.ASGARD_API_ADDRESS}/v2/apps"))
            )

        self.assertEqual(0, len(scaling_decision))
        self.assertIsNone(scale_spy)

    async def test_does_not_scale_when_difference_less_than_5_percent(self):
        cloud_interface = AsgardCloudInterface()
        state_checker = PeriodicStateChecker(cloud_interface)
        decision_maker = DecisionComponent()

        with aioresponses() as rsps:
            stats_fixture = {
                "stats": {
                    "type": "ASGARD",
                    "errors": {},
                    "cpu_pct": "0.251",
                    "ram_pct": "0.849",
                    "cpu_thr_pct": "0",
                }
            }

            apps_fixture = [
                {
                    "id": "/test_app1",
                    "cpu": 3.5,
                    "mem": 1.0,
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                    },
                }
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=apps_fixture,
            )

            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test", "version": "1.0"},
            )

            for app in apps_fixture:
                rsps.get(
                    f"{settings.ASGARD_API_ADDRESS}/apps{app['id']}/stats",
                    status=200,
                    payload=stats_fixture,
                )

            apps_stats = await state_checker.get_scalable_apps_stats()
            scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
            await cloud_interface.apply_decisions(scaling_decision)

            scale_spy = rsps.requests.get(
                ("PUT", URL(f"{settings.ASGARD_API_ADDRESS}/v2/apps"))
            )

        self.assertEqual(0, len(scaling_decision))
        self.assertEqual(1, len(apps_stats), "fetched one app")
        self.assertEqual(0, len(scaling_decision), "chose to not scale app")
        self.assertIsNone(scale_spy)

    async def test_scales_when_difference_more_than_5_percent(self):
        cloud_interface = AsgardCloudInterface()
        state_checker = PeriodicStateChecker(cloud_interface)
        decision_maker = DecisionComponent()

        with aioresponses() as rsps:
            stats_fixture = {
                "stats": {
                    "type": "ASGARD",
                    "errors": {},
                    "cpu_pct": "0.249",
                    "ram_pct": "0.851",
                    "cpu_thr_pct": "0",
                }
            }

            apps_fixture = [
                {
                    "id": "/test_app1",
                    "cpu": 3.5,
                    "mem": 1.0,
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                    },
                }
            ]

            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload=apps_fixture,
            )

            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test", "version": "1.0"},
            )

            for app in apps_fixture:
                rsps.get(
                    f"{settings.ASGARD_API_ADDRESS}/apps{app['id']}/stats",
                    status=200,
                    payload=stats_fixture,
                )

            apps_stats = await state_checker.get_scalable_apps_stats()
            scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
            await cloud_interface.apply_decisions(scaling_decision)
            scale_spy = rsps.requests.get(
                ("PUT", URL(f"{settings.ASGARD_API_ADDRESS}/v2/apps"))
            )

        self.assertEqual(1, len(apps_stats), "fetched one app")
        self.assertEqual(1, len(scaling_decision), "chose to scale the app")
        self.assertEqual(
            2.905, scaling_decision[0].cpu, "scaled cpu to the correct value"
        )
        self.assertEqual(
            1.06375,
            scaling_decision[0].mem,
            "scaled memory to the correct value",
        )
        self.assertIsNotNone(scale_spy)
