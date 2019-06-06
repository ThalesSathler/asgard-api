from asynctest import TestCase
from asgard.workers.autoscaler.cloudinterface import AsgardInterface
from aioresponses import aioresponses
from asgard.conf import settings


class FetchAppsDataTest(TestCase):
    async def test_get_all_apps_data(self):
        scaler = AsgardInterface()

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
            fixture = [
                {
                  'id': 'test_app1',
                  'labels': {
                      "asgard.autoscale.cpu": 0.3,
                      "asgard.autoscale.mem": 0.8
                  }
                },
                {
                    'id': 'test_app2',
                    'labels': {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1
                    }
                },
                {
                    'id': 'test_app3',
                    'labels': {
                        "asgard.autoscale.cpu": 0.5,
                        "asgard.autoscale.mem": 0.7
                    }
                }
            ]
            
            rsps.get(f"{settings.ASGARD_API_ADDRESS}/v2/apps", status=200, payload=fixture)
            
            apps = await scaler.get_all_scalable_apps()

            self.assertEqual(3, len(apps))
            self.assertEqual(fixture, apps)

    async def test_get_all_apps_which_should_be_scaled_no_app_should(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            fixture = [
                {
                    'id': 'test_app1',
                    'labels': {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                        "asgard.autoscale.ignore": "all"
                    }
                },
                {
                    'id': 'test_app2',
                    'labels': {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1,
                        "asgard.autoscale.ignore": "cpu;mem"
                    }
                },
                {
                    'id': 'test_app3',
                    'labels': {
                        "asgard.autoscale.cpu": 0.5,
                        "asgard.autoscale.ignore": "cpu"
                    }
                }
            ]

            rsps.get(f"{settings.ASGARD_API_ADDRESS}/v2/apps", status=200, payload=fixture)

            apps = await scaler.get_all_scalable_apps()

            self.assertEqual([], apps)
            self.assertEqual(0, len(apps))

    async def test_get_all_apps_which_should_be_scaled_one_app_should(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            fixture = [
                {
                    'id': 'test_app1',
                    'labels': {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8,
                        "asgard.autoscale.ignore": "all"
                    }
                },
                {
                    'id': 'test_app2',
                    'labels': {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1
                    }
                },
                {
                    'id': 'test_app3',
                    'labels': {
                        "asgard.autoscale.cpu": 0.5,
                        "asgard.autoscale.ignore": "cpu"
                    }
                }
            ]

            rsps.get(f"{settings.ASGARD_API_ADDRESS}/v2/apps", status=200, payload=fixture)

            apps = await scaler.get_all_scalable_apps()

            self.assertEqual(1, len(apps))
            self.assertEqual(fixture[1], apps[0])


    async def test_get_all_apps_which_should_be_scaled_one_app_should_not(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            fixture = [
                {
                    'id': 'test_app1',
                    'labels': {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8
                    }
                },
                {
                    'id': 'test_app2',
                    'labels': {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1
                    }
                },
                {
                    'id': 'test_app3',
                    'labels': {
                        "asgard.autoscale.cpu": 0.5,
                        "asgard.autoscale.ignore": "cpu"
                    }
                }
            ]

            rsps.get(f"{settings.ASGARD_API_ADDRESS}/v2/apps", status=200, payload=fixture)

            apps = await scaler.get_all_scalable_apps()

            self.assertEqual(2, len(apps))
            self.assertEqual(fixture[:2], apps)


    async def test_get_all_apps_which_should_be_scaled_some_apps_should(self):
        scaler = AsgardInterface()

        with aioresponses() as rsps:
            fixture = [
                {
                    'id': 'test_app1',
                    'labels': {
                        "asgard.autoscale.cpu": 0.3,
                        "asgard.autoscale.mem": 0.8
                    }
                },
                {
                    'id': 'test_app2',
                    'labels': {
                        "asgard.autoscale.cpu": 0.1,
                        "asgard.autoscale.mem": 0.1
                    }
                },
                {
                    'id': 'test_app3',
                    'labels': {
                        "asgard.autoscale.cpu": 0.5,
                        "asgard.autoscale.ignore": "cpu"
                    }
                },
                {
                    'id': 'test_app4',
                    'labels': {
                        "asgard.autoscale.mem": 0.2,
                        "asgard.autoscale.ignore": "mem"
                    }
                }
            ]

            rsps.get(f"{settings.ASGARD_API_ADDRESS}/v2/apps", status=200, payload=fixture)

            apps = await scaler.get_all_scalable_apps()

            self.assertEqual(2, len(apps))
            self.assertEqual(fixture[:2], apps)

