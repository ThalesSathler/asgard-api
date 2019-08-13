from aioresponses import aioresponses
from asynctest import TestCase
from yarl import URL

from asgard.conf import settings
from asgard.workers.autoscaler.asgard_cloudinterface import AsgardInterface
from asgard.workers.models.decision import Decision
from asgard.workers.models.scalable_app import ScalableApp


class TestScaleApps(TestCase):
    async def test_tune_everything_in_one_app(self):
        interface = AsgardInterface()
        app = ScalableApp("test")
        decisions = [Decision(app.id, cpu=0.3, mem=9)]

        with aioresponses() as rsps:
            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test1", "version": "1.0"},
            )
            applied_decisions = await interface.apply_decisions(decisions)

        self.assertEqual(len(applied_decisions), 1)
        self.assertEqual(applied_decisions[0]["id"], decisions[0].id)
        self.assertEqual(applied_decisions[0]["cpus"], decisions[0].cpu)
        self.assertEqual(applied_decisions[0]["mem"], decisions[0].mem)

    async def test_tune_everything_in_multiple_apps(self):
        interface = AsgardInterface()
        app1 = ScalableApp("test1")
        app2 = ScalableApp("test2")
        app3 = ScalableApp("test3")

        decisions = [
            Decision(app1.id, cpu=0.2, mem=10),
            Decision(app2.id, cpu=0.4, mem=20),
            Decision(app3.id, cpu=0.1, mem=9),
        ]

        with aioresponses() as rsps:
            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test2", "version": "1.0"},
            )
            applied_decisions = await interface.apply_decisions(decisions)

        self.assertEqual(len(applied_decisions), 3)
        for i in range(len(decisions)):
            self.assertEqual(applied_decisions[i]["id"], decisions[i].id)
            self.assertEqual(applied_decisions[i]["cpus"], decisions[i].cpu)
            self.assertEqual(applied_decisions[i]["mem"], decisions[i].mem)

    async def test_tune_one_thing_in_one_app(self):
        interface = AsgardInterface()
        app = ScalableApp("test")
        decisions = [Decision(app.id, cpu=0.3)]

        with aioresponses() as rsps:
            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test1", "version": "1.0"},
            )
            applied_decisions = await interface.apply_decisions(decisions)

        self.assertEqual(len(applied_decisions), 1)
        self.assertEqual(applied_decisions[0]["id"], decisions[0].id)
        self.assertEqual(applied_decisions[0]["cpus"], decisions[0].cpu)
        self.assertEqual("mem" in applied_decisions[0], False)

    async def test_tune_multiple_apps_with_different_params(self):
        interface = AsgardInterface()
        app1 = ScalableApp("test1")
        app2 = ScalableApp("test2")
        app3 = ScalableApp("test3")

        decisions = [
            Decision(app1.id, mem=10),
            Decision(app2.id, cpu=0.4),
            Decision(app3.id, cpu=0.1, mem=9),
        ]

        with aioresponses() as rsps:
            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test2", "version": "1.0"},
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

    async def test_http_request_is_sent_with_correct_parameters(self):
        interface = AsgardInterface()

        decisions = [Decision("test", mem=64, cpu=0.4)]

        body_fixture = [{"id": "test", "mem": 64, "cpus": 0.4}]
        headers_fixture = {
            "Content-Type": "application/json",
            "Authorization": f"Token {settings.AUTOSCALER_AUTH_TOKEN}",
        }

        with aioresponses() as rsps:
            rsps.put(
                f"{settings.ASGARD_API_ADDRESS}/v2/apps",
                status=200,
                payload={"deploymentId": "test", "version": "1.0"},
            )

            await interface.apply_decisions(decisions)
            calls = rsps.requests.get(
                ("PUT", URL(f"{settings.ASGARD_API_ADDRESS}/v2/apps"))
            )

            self.assertIsNotNone(calls)
            self.assertEqual(body_fixture, calls[0].kwargs.get("json"))
            self.assertEqual(headers_fixture, calls[0].kwargs.get("headers"))
