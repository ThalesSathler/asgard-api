from aioresponses import aioresponses
from asynctest import TestCase

from asgard.conf import settings
from asgard.workers.autoscaler.cloudinterface import AsgardInterface
from asgard.workers.models.scalable_app import ScalableApp
from asgard.workers.models.scaling_decision import Decision


class ScaleAppsTest(TestCase):
    async def test_tune_everything_in_one_app(self):
        app_fixture = {
            "id": "test_app1",
            "cpu": 3.5,
            "mem": 1.0,
            "labels": {
                "asgard.autoscale.cpu": 0.1,
                "asgard.autoscale.mem": 0.5,
            },
        }

        interface = AsgardInterface()
        app = ScalableApp(**app_fixture)
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
            applied_decisions = await interface.apply_decisions(decisions)

        self.assertEqual(len(applied_decisions), 1)
        self.assertEqual(applied_decisions[0]["id"], decisions[0].id)
        self.assertEqual(applied_decisions[0]["cpus"], decisions[0].cpu)
        self.assertEqual(applied_decisions[0]["mem"], decisions[0].mem)

    async def test_tune_everything_in_multiple_apps(self):
        apps_fixture = [
            {
                "id": "test_app1",
                "cpu": 3.0,
                "mem": 0.5,
                "labels": {
                    "asgard.autoscale.cpu": 0.3,
                    "asgard.autoscale.mem": 0.8,
                },
            },
            {
                "id": "test_app2",
                "cpu": 3.0,
                "mem": 0.5,
                "labels": {
                    "asgard.autoscale.cpu": 0.1,
                    "asgard.autoscale.mem": 0.1,
                },
            },
            {
                "id": "test_app3",
                "cpu": 3.0,
                "mem": 0.5,
                "labels": {
                    "asgard.autoscale.cpu": 0.5,
                },
            }
        ]

        app1 = ScalableApp(**apps_fixture[0])
        app2 = ScalableApp(**apps_fixture[1])
        app3 = ScalableApp(**apps_fixture[2])

        interface = AsgardInterface()

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
            applied_decisions = await interface.apply_decisions(decisions)

        self.assertEqual(len(applied_decisions), 3)
        for i in range(len(decisions)):
            self.assertEqual(applied_decisions[i]["id"], decisions[i].id)
            self.assertEqual(applied_decisions[i]["cpus"], decisions[i].cpu)
            self.assertEqual(applied_decisions[i]["mem"], decisions[i].mem)

    async def test_tune_one_thing_in_one_app(self):
        app_fixture = {
            "id": "test_app1",
            "cpu": 3.5,
            "mem": 1.0,
            "labels": {
                "asgard.autoscale.cpu": 0.1,
                "asgard.autoscale.mem": 0.5,
            },
        }

        app = ScalableApp(**app_fixture)

        interface = AsgardInterface()

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
            applied_decisions = await interface.apply_decisions(decisions)

        self.assertEqual(len(applied_decisions), 1)
        self.assertEqual(applied_decisions[0]["id"], decisions[0].id)
        self.assertEqual(applied_decisions[0]["cpus"], decisions[0].cpu)
        self.assertEqual("mem" in applied_decisions[0], False)

    async def test_tune_multiple_apps_with_different_params(self):
        apps_fixture = [
            {
                "id": "test_app1",
                "cpu": 3.0,
                "mem": 0.5,
                "labels": {
                    "asgard.autoscale.cpu": 0.3,
                    "asgard.autoscale.mem": 0.8,
                },
            },
            {
                "id": "test_app2",
                "cpu": 3.0,
                "mem": 0.5,
                "labels": {
                    "asgard.autoscale.cpu": 0.1,
                    "asgard.autoscale.mem": 0.1,
                },
            },
            {
                "id": "test_app3",
                "cpu": 3.0,
                "mem": 0.5,
                "labels": {
                    "asgard.autoscale.cpu": 0.5,
                },
            }
        ]

        app1 = ScalableApp(**apps_fixture[0])
        app2 = ScalableApp(**apps_fixture[1])
        app3 = ScalableApp(**apps_fixture[2])

        interface = AsgardInterface()

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
            applied_decisions = await interface.apply_decisions(decisions)

        self.assertEqual(len(applied_decisions), 3)

        self.assertEqual(applied_decisions[0]["id"], decisions[0].id)
        self.assertEqual(applied_decisions[0]["mem"], decisions[0].mem)
        self.assertEqual("cpus" in applied_decisions[0], False)

        self.assertEqual(applied_decisions[1]["id"], decisions[1].id)
        self.assertEqual(applied_decisions[1]["cpus"], decisions[1].cpu)
        self.assertEqual("mem" in applied_decisions[1], False)

        self.assertEqual(applied_decisions[2]["id"], decisions[2].id)
        self.assertEqual(applied_decisions[2]["mem"], decisions[2].mem)
        self.assertEqual(applied_decisions[2]["cpus"], decisions[2].cpu)
