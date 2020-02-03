import json
from copy import deepcopy
from unittest.mock import ANY, MagicMock, patch

from marathon import MarathonApp
from responses import RequestsMock

from asgard.models.account import AccountDB
from asgard.models.user import UserDB
from hollowman import conf
from hollowman.app import application
from hollowman.http_wrappers.request import Request
from hollowman.request_handlers import new
from itests.util import BaseTestCase
from tests.utils import with_json_fixture


class RequestHandlersTests(BaseTestCase):
    async def setUp(self):
        await super(RequestHandlersTests, self).setUp()
        self.request_apps = [
            (MarathonApp(id="/xablau"), MarathonApp(id="/xena")),
            (MarathonApp(id="/foo"), MarathonApp(id="/bar")),
        ]

        self.user = UserDB(
            tx_email="user@host.com.br",
            tx_name="John Doe",
            tx_authkey="69ed620926be4067a36402c3f7e9ddf0",
        )
        self.account_dev = AccountDB(
            id=4, name="Dev Team", namespace="dev", owner="company"
        )
        self.user.accounts = [self.account_dev]

    def test_it_call_dispatch_using_user_from_request(self):
        """
        Certificamos que o user preenchido no request é repassado para o dispatch
        """
        with application.test_request_context(
            "/v2/apps/foo", method="GET"
        ) as ctx:
            with patch("hollowman.request_handlers.upstream_request"), patch(
                "hollowman.request_handlers.dispatch"
            ) as dispatch_mock:
                user = MagicMock()
                ctx.request.user = user
                request_parser = Request(ctx.request)
                request_parser.split = MagicMock(
                    return_value=[self.request_apps[0]]
                )
                request_parser.join = MagicMock()
                response = new(request_parser)
                dispatch_mock.assert_called_once_with(user=user, request=ANY)

    @with_json_fixture("../fixtures/single_full_app.json")
    def test_versions_endpoint_returns_app_on_root_json(
        self, single_full_app_fixture
    ):
        """
        Apesar de um GET /v2/apps/<app-id> retornat a app em:
            {"app": <app-definition}
        um GET /v2/apps/<app-id>/versions/<version-id> retorna em:
            {<app-definition>}

        Aqui conferimos que nosso pipeline retorna um response consistente com
        essa regra
        """
        auth_header = {
            "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
        }
        single_full_app_fixture["id"] = "/dev/foo"
        with application.test_client() as client:
            with RequestsMock() as rsps:
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0]
                    + "/v2/apps/dev/foo/versions/2017-10-31T13:01:07.768Z",
                    body=json.dumps(single_full_app_fixture),
                    status=200,
                )
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0] + "/v2/apps//dev/foo",
                    body=json.dumps({"app": single_full_app_fixture}),
                    status=200,
                )
                response = client.get(
                    "/v2/apps/foo/versions/2017-10-31T13:01:07.768Z",
                    headers=auth_header,
                )
                self.assertEqual(200, response.status_code)
                self.assertEqual("/foo", json.loads(response.data)["id"])

    @with_json_fixture("../fixtures/single_full_app.json")
    def test_apps_endpoint_accepts_app_with_versions_in_the_name(
        self, single_full_app_fixture
    ):
        """
        Regressão: Commit 0068801288b33a407676a6aa9b521881854de2f7
        Devemos aceitar uma app que possui a string "versions" em um lugar no nome, especialmente no fim
        de uma parte do path, ex: "/workers/conversions/splitter"
        """
        auth_header = {
            "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
        }
        single_full_app_fixture["id"] = "/dev/workers/conversions/splitter"
        with application.test_client() as client:
            with RequestsMock() as rsps:
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0]
                    + "/v2/apps/dev/workers/conversions/splitter",
                    body=json.dumps({"app": single_full_app_fixture}),
                    status=200,
                )
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0]
                    + "/v2/apps//dev/workers/conversions/splitter",
                    body=json.dumps({"app": single_full_app_fixture}),
                    status=200,
                )
                response = client.get(
                    "/v2/apps/workers/conversions/splitter", headers=auth_header
                )
                self.assertEqual(200, response.status_code)
                self.assertTrue("app" in json.loads(response.data))
                self.assertEqual(
                    "/workers/conversions/splitter",
                    json.loads(response.data)["app"]["id"],
                )

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_groups_endpoint_returns_group_on_root_json(
        self, group_dev_namespace_fixture
    ):
        auth_header = {
            "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
        }
        with application.test_client() as client:
            with RequestsMock() as rsps:
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0] + "/v2/groups//dev/group-b",
                    body=json.dumps(
                        deepcopy(group_dev_namespace_fixture["groups"][1])
                    ),
                    status=200,
                )
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0] + "/v2/groups/dev/group-b",
                    body=json.dumps(
                        deepcopy(group_dev_namespace_fixture["groups"][1])
                    ),
                    status=200,
                )
                response = client.get("/v2/groups/group-b", headers=auth_header)
                self.assertEqual(200, response.status_code)
                self.assertEqual("/group-b", json.loads(response.data)["id"])

    @with_json_fixture("../fixtures/queue/get.json")
    def test_queue_removes_queued_appps_from_other_namespaces(
        self, queue_get_fixture
    ):
        """
        Removemos todas as apps que não sejam do namespace atual.
        Esse teste tambéem confirma que o namespace é removido dos elementos
        que voltam no response.
        """
        auth_header = {
            "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
        }
        with application.test_client() as client:
            with RequestsMock() as rsps:
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0] + "/v2/queue",
                    status=200,
                    json=queue_get_fixture,
                )

                response = client.get("/v2/queue", headers=auth_header)
                self.assertEqual(200, response.status_code)
                response_data = json.loads(response.data)
                self.assertEqual(1, len(response_data["queue"]))
                self.assertEqual(
                    "/waiting", response_data["queue"][0]["app"]["id"]
                )

    def test_get_empty_apps_listing(self):
        auth_header = {
            "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
        }
        with application.test_client() as client:
            with RequestsMock() as rsps:
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0] + "/v2/groups//dev/",
                    body=json.dumps({"apps": []}),
                    status=200,
                )
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0] + "/v2/apps",
                    body=json.dumps({"apps": []}),
                    status=200,
                )
                response = client.get("/v2/apps", headers=auth_header)
                self.assertEqual(200, response.status_code)
                response_body = json.loads(response.data)
                self.assertEqual({"apps": []}, response_body)


class DispatchResponse404Test(BaseTestCase):
    async def setUp(self):
        await super(DispatchResponse404Test, self).setUp()
        self.user = UserDB(
            tx_email="user@host.com.br",
            tx_name="John Doe",
            tx_authkey="69ed620926be4067a36402c3f7e9ddf0",
        )
        self.account_dev = AccountDB(
            id=4, name="Dev Team", namespace="dev", owner="company"
        )
        self.user.accounts = [self.account_dev]

    def test_do_not_dispatch_response_pipeline_if_upstream_returns_404(self):
        auth_header = {
            "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
        }
        with application.test_client() as client:
            with RequestsMock() as rsps:
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0] + "/v2/apps//dev/foo",
                    body=json.dumps({"message": "App /foo not found"}),
                    status=404,
                )
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0] + "/v2/apps/dev/foo",
                    body=json.dumps({"message": "App /foo not found"}),
                    status=404,
                )
                response = client.get("/v2/apps/foo", headers=auth_header)
                self.assertEqual(404, response.status_code)

    @with_json_fixture("../fixtures/single_full_app_with_http_labels.json")
    def test_disables_http_when_suspending_app(self, single_full_app_fixture):
        auth_header = {
            "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
        }
        app_id = "/dev/my-app"
        single_full_app_fixture["id"] = app_id
        single_full_app_fixture["instances"] = 0  # Suspend app

        expected_labels = single_full_app_fixture["labels"].copy()
        expected_labels["traefik.enable"] = False

        with application.test_client() as client:
            with RequestsMock() as rsps:
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0] + f"/v2/apps//dev{app_id}",
                    body=json.dumps({"app": single_full_app_fixture}),
                    status=200,
                )

                rsps.add(
                    method="POST",
                    url=conf.MARATHON_ADDRESSES[0] + f"/v2/apps{app_id}",
                    body=json.dumps(
                        {**single_full_app_fixture, "labels": expected_labels}
                    ),
                    status=200,
                )
                response = client.post(
                    f"/v2/apps{app_id}",
                    headers=auth_header,
                    json=single_full_app_fixture,
                )
                self.assertEqual(200, response.status_code)
