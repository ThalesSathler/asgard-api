from aioresponses import aioresponses
from asynctest import TestCase

from asgard.conf import settings
from asgard.workers.autoscaler.cloudinterface import AsgardInterface
from asgard.workers.models.scalable_app import ScalableApp
from asgard.workers.models.scaling_decision import Decision


class ScaleAppsTest(TestCase):
    async def test_tune_everything_in_one_app(self):
        interface = AsgardInterface()
        app = ScalableApp("test")
        decisions = [Decision(app.id, cpu=0.3, mem=9)]

        with aioresponses() as rsps:
            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={
                    "deploymentId": "test1",
                    "version": "1.0"
                }
            )
            new_app_stats = await interface.apply_decisions(decisions)

        self.assertEqual(len(new_app_stats), 1)
        self.assertEqual(new_app_stats[0].id, "test")

    async def test_tune_everything_in_multiple_apps(self):
        interface = AsgardInterface()
        app1 = ScalableApp("test1")
        app2 = ScalableApp("test2")
        app3 = ScalableApp("test3")

        decisions = [
            Decision(app1.id, cpu=0.2, mem=10),
            Decision(app2.id, cpu=0.4, mem=20),
            Decision(app3.id, cpu=0.1, mem=9)
        ]

        with aioresponses() as rsps:
            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={
                    "deploymentId": "test2",
                    "version": "1.0"
                }
            )
            new_apps_stats = await interface.apply_decisions(decisions)

        self.assertEqual(len(new_apps_stats), 3)
        self.assertEqual(new_apps_stats[0].id, "test1")
        self.assertEqual(new_apps_stats[1].id, "test2")
        self.assertEqual(new_apps_stats[2].id, "test3")

    async def test_tune_one_thing_in_one_app(self):
        interface = AsgardInterface()
        app = ScalableApp("test")
        decisions = [Decision(app.id, cpu=0.3)]

        with aioresponses() as rsps:
            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={
                    "deploymentId": "test1",
                    "version": "1.0"
                }
            )
            new_app_stats = await interface.apply_decisions(decisions)

        self.assertEqual(len(new_app_stats), 1)
        self.assertEqual(new_app_stats[0].id, "test")

    async def test_tune_multiple_apps_with_different_params(self):
        interface = AsgardInterface()
        app1 = ScalableApp("test1")
        app2 = ScalableApp("test2")
        app3 = ScalableApp("test3")

        decisions = [
            Decision(app1.id, mem=10),
            Decision(app2.id, cpu=0.4),
            Decision(app3.id, cpu=0.1, mem=9)
        ]

        with aioresponses() as rsps:
            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={
                    "deploymentId": "test2",
                    "version": "1.0"
                }
            )
            new_apps_stats = await interface.apply_decisions(decisions)

        self.assertEqual(len(new_apps_stats), 3)
        self.assertEqual(new_apps_stats[0].id, "test1")
        self.assertEqual(new_apps_stats[1].id, "test2")
        self.assertEqual(new_apps_stats[2].id, "test3")
