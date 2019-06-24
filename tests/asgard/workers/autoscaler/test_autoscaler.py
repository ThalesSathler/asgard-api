from aioresponses import aioresponses
from asynctest import TestCase

from asgard.conf import settings
from asgard.workers.autoscaler.cloudinterface import (
    AsgardInterface as AsgardCloudInterface,
)
from asgard.workers.autoscaler.decisioncomponent import DecisionComponent
from asgard.workers.autoscaler.periodicstatechecker import PeriodicStateChecker


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
                    "id": "test_app1",
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                        "asgard.autoscale.ignore": "all",
                    },
                },
                {
                    "id": "/test_app2",
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

            # for app in apps_fixture:
            rsps.get(
                f"{settings.ASGARD_API_ADDRESS}/apps/test_app2/stats",
                status=200,
                payload=stats_fixture,
            )

            apps_stats = await state_checker.get_scalable_apps_stats()
            scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
            # cloud_interface.scale_apps(scaling_decision)

            self.assertEqual(1, len(scaling_decision))

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
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                        "asgard.autoscale.ignore": "cpu",
                    },
                },
                {
                    "id": "/test_app2",
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

            apps_stats = await state_checker.get_scalable_apps_stats()
            scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
        # cloud_interface.scale_apps(scaling_decision)

        self.assertEqual(len(apps_stats), len(scaling_decision))

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
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                        "asgard.autoscale.ignore": "all",
                    },
                },
                {
                    "id": "/test_app2",
                    "labels": {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1,
                        "asgard.autoscale.ignore": "",
                    },
                },
                {
                    "id": "/test_app3",
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

            apps_stats = await state_checker.get_scalable_apps_stats()
            scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
        # cloud_interface.scale_apps(scaling_decision)

        self.assertEqual(2, len(scaling_decision))

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
                    "labels": {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                        "asgard.autoscale.ignore": "all",
                    },
                },
                {
                    "id": "/test_app2",
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

            for app in apps_fixture:
                rsps.get(
                    f"{settings.ASGARD_API_ADDRESS}/apps{app['id']}/stats",
                    status=200,
                    payload=stats_fixture,
                )

            apps_stats = await state_checker.get_scalable_apps_stats()
            scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
        # cloud_interface.scale_apps(scaling_decision)

        self.assertEqual(0, len(apps_stats))
