from aioresponses import aioresponses

from asgard.api import agents
from asgard.app import app
from asgard.models.account import AccountDB
from asgard.models.user import UserDB
from asgard.models.user_has_account import UserHasAccount
from itests.util import BaseTestCase
from tests.conf import TEST_LOCAL_AIOHTTP_ADDRESS
from tests.utils import ClusterOptions, build_mesos_cluster


class AgentsApiEndpointTest(BaseTestCase):
    async def setUp(self):
        await super(AgentsApiEndpointTest, self).setUp()
        self.client = await self.aiohttp_client(app)
        self.user_auth_key = "c0c0b73b18864550a3e3b93a59c4b7d8"

    def _prepare_additional_fixture_data(self):
        self.pg_data_mocker.add_data(
            UserDB,
            ["id", "tx_name", "tx_email", "tx_authkey"],
            [
                [
                    128,
                    "User for Infra Account",
                    "user-infra@host.com",
                    self.user_auth_key,
                ]
            ],
        )

        self.pg_data_mocker.add_data(
            AccountDB,
            ["id", "name", "namespace", "owner"],
            [[40, "Dev Team", "infra", "asgard-infra"]],
        )

        self.pg_data_mocker.add_data(
            UserHasAccount, ["id", "user_id", "account_id"], [[50, 128, 40]]
        )

    async def tearDown(self):
        await super(AgentsApiEndpointTest, self).tearDown()

    async def test_agents_list_should_return_only_agents_from_specific_account(
        self
    ):
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(
                rsps,
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S44",
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S10",  # namespace=asgard
            )
            resp = await self.client.get(
                "/agents",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(1, len(data["agents"]))
            self.assertEqual(
                set(["dev"]),
                set([agent["attributes"]["owner"] for agent in data["agents"]]),
            )
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S44",
                data["agents"][0]["id"],
            )
            self.assertEqual("MESOS", data["agents"][0]["type"])
            self.assertEqual(
                {"cpu_pct": "38.72", "ram_pct": "25.79"},
                data["agents"][0]["stats"],
            )
            self.assertEqual(
                {"cpu_pct": "38.72", "ram_pct": "25.79"}, data["stats"]
            )
            self.assertEqual(0, data["agents"][0]["total_apps"])

    async def test_agents_list_includes_app_list(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(
                rsps,
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S3",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S10",  # namespace=asgard
            )
            resp = await self.client.get(
                "/agents",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(2, len(data["agents"]))
            self.assertEqual(
                set(["asgard-infra"]),
                set([agent["attributes"]["owner"] for agent in data["agents"]]),
            )
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",
                data["agents"][0]["id"],
            )
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S3",
                data["agents"][1]["id"],
            )
            self.assertEqual("MESOS", data["agents"][0]["type"])

            self.assertEqual(5, data["agents"][0]["total_apps"])
            expected_app_ids = sorted(
                [
                    "infra/asgard/api",
                    "infra/rabbitmq",
                    "captura/kirby/feeder",
                    "portal/api",
                    "captura/wetl/visitcentral",
                ]
            )
            self.assertEqual(
                expected_app_ids,
                sorted(
                    [app["id"] for app in data["agents"][0]["applications"]]
                ),
            )

            self.assertEqual(0, data["agents"][1]["total_apps"])
            expected_app_ids_agent_s3 = sorted([])
            self.assertEqual(
                expected_app_ids_agent_s3,
                sorted(
                    [app["id"] for app in data["agents"][1]["applications"]]
                ),
            )

    async def test_agents_list_should_populate_errors_for_each_field(self):
        """
        Cada campo que tiver dado problema no momento de ser preenchido estará no
        campo {"errors": {...}} onde a key é o nome do campo e o value é a mensagem de erro.
        """

        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(
                rsps,
                {
                    "id": "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",
                    "apps": ClusterOptions.CONNECTION_ERROR,
                },  # namespace=asgard-infra
                {
                    "id": "ead07ffb-5a61-42c9-9386-21b680597e6c-S3"
                },  # namespace=asgard-infra
                {
                    "id": "ead07ffb-5a61-42c9-9386-21b680597e6c-S10"
                },  # namespace=asgard
            )

            resp = await self.client.get(
                "/agents",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(2, len(data["agents"]))
            self.assertEqual(
                set(["asgard-infra"]),
                set([agent["attributes"]["owner"] for agent in data["agents"]]),
            )
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",
                data["agents"][0]["id"],
            )
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S3",
                data["agents"][1]["id"],
            )
            self.assertEqual("MESOS", data["agents"][0]["type"])
            self.assertEqual(0, data["agents"][0]["total_apps"])
            self.assertEqual([], data["agents"][0]["applications"])
            self.assertTrue(
                "INDISPONIVEL" in data["agents"][0]["errors"]["total_apps"]
            )

    async def test_agents_with_attrs_empty_response(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()

        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(
                rsps,
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S44",
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S10",  # namespace=asgard
            )
            resp = await self.client.get(
                "/agents/with-attrs?tag1=not-found",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(
                {"agents": [], "stats": {"cpu_pct": "0.00", "ram_pct": "0.00"}},
                data,
            )

    async def test_agents_with_atrrs_one_attr_filter(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()

        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(
                rsps,
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S3",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S4",  # namespace=asgard-dev
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S44",  # namespace=dev
            )
            resp = await self.client.get(
                "/agents/with-attrs?workload=general",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(2, len(data["agents"]))
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",
                data["agents"][0]["id"],
            )
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S3",
                data["agents"][1]["id"],
            )

            self.assertEqual(
                {"cpu_pct": "44.76", "ram_pct": "45.46"}, data["stats"]
            )

    async def test_agents_with_atrrs_one_attr_filter_with_account_id(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()

        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(
                rsps,
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S3",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S4",  # namespace=asgard-dev
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S44",  # namespace=dev
            )
            resp = await self.client.get(
                "/agents/with-attrs?workload=general&account_id=40",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(2, len(data["agents"]))
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",
                data["agents"][0]["id"],
            )
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S3",
                data["agents"][1]["id"],
            )

    async def test_agents_with_atrrs_two_attrs_filter(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()

        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(
                rsps,
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S3",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S4",  # namespace=asgard-dev
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S44",  # namespace=dev
            )
            resp = await self.client.get(
                "/agents/with-attrs?workload=general&dc=gcp",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(1, len(data["agents"]))
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",
                data["agents"][0]["id"],
            )

    async def test_agents_with_atrrs_includes_app_list(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()

        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(
                rsps,
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S3",  # namespace=asgard-infra
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S4",  # namespace=asgard-dev
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S44",  # namespace=dev
            )
            resp = await self.client.get(
                "/agents/with-attrs?workload=general&dc=gcp",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(1, len(data["agents"]))
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",
                data["agents"][0]["id"],
            )
            self.assertEqual(5, data["agents"][0]["total_apps"])
            expected_app_ids = sorted(
                [
                    "infra/asgard/api",
                    "infra/rabbitmq",
                    "captura/kirby/feeder",
                    "portal/api",
                    "captura/wetl/visitcentral",
                ]
            )
            self.assertEqual(
                expected_app_ids,
                sorted(
                    [app["id"] for app in data["agents"][0]["applications"]]
                ),
            )

    async def test_agent_app_list_zero_apps_running(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()

        slave_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S3"
        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(rsps, slave_id)
            resp = await self.client.get(
                f"/agents/{slave_id}/apps",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(0, len(data["apps"]))

    async def test_agent_app_list_apps_running(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()

        with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
            build_mesos_cluster(rsps, "ead07ffb-5a61-42c9-9386-21b680597e6c-S0")
            resp = await self.client.get(
                "/agents/ead07ffb-5a61-42c9-9386-21b680597e6c-S0/apps",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(5, len(data["apps"]))
            expected_app_ids = sorted(
                [
                    "captura/wetl/visitcentral",
                    "portal/api",
                    "captura/kirby/feeder",
                    "infra/asgard/api",
                    "infra/rabbitmq",
                ]
            )
            self.assertEqual(
                expected_app_ids, sorted([app["id"] for app in data["apps"]])
            )
