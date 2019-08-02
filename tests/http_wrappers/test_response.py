import json
import unittest
from copy import deepcopy
from http import HTTPStatus
from unittest.mock import call, patch

from flask import Response as FlaskResponse
from marathon import MarathonApp
from marathon.models.group import MarathonGroup
from marathon.models.task import MarathonTask

from asgard.models.account import AccountDB as Account
from hollowman.app import application
from hollowman.http_wrappers import Response
from hollowman.marathon.group import AsgardAppGroup
from hollowman.marathonapp import AsgardApp
from hollowman.models import User
from tests.utils import with_json_fixture


class ResponseTest(unittest.TestCase):
    def test_remove_namespace_if_exists(self):
        response = Response(None, None)
        self.assertEqual("", response._remove_namespace_if_exists("dev", ""))
        self.assertEqual("/", response._remove_namespace_if_exists("dev", "/"))
        self.assertEqual(
            "/", response._remove_namespace_if_exists("dev", "/dev/")
        )
        self.assertEqual(
            "", response._remove_namespace_if_exists("dev", "/dev")
        )
        self.assertEqual(
            "/foo", response._remove_namespace_if_exists("dev", "/dev/foo")
        )
        self.assertEqual(
            "/foo/dev",
            response._remove_namespace_if_exists("dev", "/dev/foo/dev"),
        )
        self.assertEqual(
            "/dev", response._remove_namespace_if_exists("dev", "/dev/dev")
        )
        self.assertEqual(
            None, response._remove_namespace_if_exists("dev", None)
        )


class SplitTests(unittest.TestCase):
    def setUp(self):
        self.empty_ok_response = FlaskResponse(
            response=b"{}", status=HTTPStatus.OK, headers={}
        )
        self.user = User(tx_name="User One", tx_email="user@host.com")
        self.user.current_account = Account(
            name="Dev", namespace="dev", owner="company"
        )

    @with_json_fixture("single_full_app.json")
    def test_a_single_app_response_returns_a_single_marathonapp(self, fixture):
        with application.test_request_context(
            "/v2/apps//foo", method="GET", data=b""
        ) as ctx:
            flask_response = FlaskResponse(
                response=json.dumps({"app": fixture}),
                status=HTTPStatus.OK,
                headers={},
            )
            response = Response(ctx.request, flask_response)

            with patch.object(response, "marathon_client") as client:
                client.get_app.return_value = AsgardApp.from_json(fixture)
                apps = list(response.split())
                self.assertEqual([call("/foo")], client.get_app.call_args_list)

            self.assertEqual(
                apps,
                [(AsgardApp.from_json(fixture), client.get_app.return_value)],
            )

    @with_json_fixture("single_full_app.json")
    def test_multiapp_response_returns_multiple_marathonapp_instances(
        self, fixture
    ):
        modified_app = fixture.copy()
        modified_app["id"] = "/xablau"

        apps = [fixture, modified_app]
        with application.test_request_context(
            "/v2/apps/", method="GET", data=b""
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps({"apps": apps}),
                status=HTTPStatus.OK,
                headers={},
            )
            response = Response(ctx.request, response)

        with patch.object(response, "marathon_client") as client:
            original_apps = [MarathonApp.from_json(app) for app in apps]
            client.get_app.side_effect = original_apps
            apps = list(response.split())

        self.assertEqual(
            apps,
            [
                (AsgardApp.from_json(fixture), original_apps[0]),
                (AsgardApp.from_json(modified_app), original_apps[1]),
            ],
        )

    @with_json_fixture("single_full_app.json")
    def test_a_response_for_restart_operation_with_appid_in_url_path_does_not_split_response(
        self, fixture
    ):
        """
        Quando o response retorna um Deployment, não fazemos split.
        """
        with application.test_request_context(
            "/v2/apps/xablau/restart", method="PUT", data=b'{"force": true}'
        ) as ctx:
            response = FlaskResponse(
                response=b"{}", status=HTTPStatus.OK, headers={}
            )
            response = Response(ctx.request, response)
            apps = list(response.split())
            self.assertEqual(0, len(apps))

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_split_groups_read_on_root_group(self, group_dev_namespace_fixture):
        with application.test_request_context(
            "/v2/groups/", method="GET"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture),
                status=HTTPStatus.OK,
                headers={},
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            groups_tuple = list(response.split())
            self.assertEqual(5, len(groups_tuple))
            expected_groups = [
                AsgardAppGroup(g)
                for g in AsgardAppGroup(
                    MarathonGroup.from_json(group_dev_namespace_fixture)
                ).iterate_groups()
            ]
            # Compara com os groups originais
            self.assertEqual(expected_groups, [g[1] for g in groups_tuple])

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_split_group_nonroot_empty_group(self, group_dev_namespace_fixture):
        with application.test_request_context(
            "/v2/groups/group-c", method="GET"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture["groups"][2]),
                status=HTTPStatus.OK,
                headers={},
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            groups_tuple = list(response.split())
            self.assertEqual(1, len(groups_tuple))
            expected_groups = [
                AsgardAppGroup(g)
                for g in AsgardAppGroup(
                    MarathonGroup.from_json(
                        group_dev_namespace_fixture["groups"][2]
                    )
                ).iterate_groups()
            ]
            # Compara com os groups originais
            self.assertEqual(expected_groups, [g[1] for g in groups_tuple])

    @unittest.skip("A ser implementado")
    def test_split_groups_write_PUT_on_group(self):
        self.fail()

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_split_groups_read_on_specific_group(
        self, group_dev_namespace_fixture
    ):
        with application.test_request_context(
            "/v2/groups/group-b", method="GET"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture["groups"][1]),
                status=HTTPStatus.OK,
                headers={},
            )
            ctx.request.user = self.user
            response = Response(ctx.request, response)
            groups_tuple = list(response.split())
            self.assertEqual(2, len(groups_tuple))
            expected_groups = [
                AsgardAppGroup(g)
                for g in AsgardAppGroup(
                    MarathonGroup.from_json(
                        group_dev_namespace_fixture["groups"][1]
                    )
                ).iterate_groups()
            ]
            # Compara com os groups originais
            self.assertEqual(expected_groups, [g[1] for g in groups_tuple])

    @with_json_fixture("../fixtures/tasks/get.json")
    def test_split_tasks_GET(self, tasks_get_fixture):
        """
        No cado de um GET, o retorno sempre é uma lista de apps.
        """
        with application.test_request_context(
            "/v2/tasks/", method="GET"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps(tasks_get_fixture), status=HTTPStatus.OK
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            tasks_tuple = list(response.split())

            self.assertEqual(
                [
                    MarathonTask.from_json(task)
                    for task in tasks_get_fixture["tasks"]
                ],
                [task[0] for task in tasks_tuple],
            )

    @with_json_fixture("../fixtures/tasks/get.json")
    def test_split_staks_POST_scale_false(self, tasks_get_fixture):
        """
        No caso do POST com `?scale=false` o retorno é:
            - Lista de apps que foram killed
        Por isso usamos a fixture de tasks/get.json aqui
        """
        with application.test_request_context(
            "/v2/tasks/delete?scale=false", method="POST"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps(tasks_get_fixture), status=HTTPStatus.OK
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            tasks_tuple = list(response.split())

            self.assertEqual(
                [
                    MarathonTask.from_json(task)
                    for task in tasks_get_fixture["tasks"]
                ],
                [task[0] for task in tasks_tuple],
            )

    @with_json_fixture("../fixtures/tasks/post?scale=true.json")
    def test_split_staks_POST_scale_true(self, tasks_post_fixture):
        """
        No caso do POST com `?scale=true` o retorno é:
            - Deployment Id
        Isso significa que não faremos split do response
        """
        with application.test_request_context(
            "/v2/tasks/delete?scale=true", method="POST"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps(tasks_post_fixture), status=HTTPStatus.OK
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            tasks_tuple = list(response.split())
            self.assertEqual(0, len(tasks_tuple))

    @with_json_fixture("../fixtures/queue/get.json")
    def test_split_queue_GET(self, queue_get_fixture):
        with application.test_request_context("/v2/queue", method="GET") as ctx:
            response = FlaskResponse(
                response=json.dumps(queue_get_fixture), status=HTTPStatus.OK
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            queue_tuples = list(response.split())
            self.assertEqual(2, len(queue_tuples))


class JoinTests(unittest.TestCase):
    def setUp(self):
        self.user = User(tx_name="User One", tx_email="user@host.com")
        self.user.current_account = Account(
            name="Dev", namespace="dev", owner="company"
        )

    def test_join_a_uknown_response(self):
        """
        Como o repsonse roda para qualquer requiest que retornou 200 no upstream,
        muitas vezes pode passar por ele um request que ele "não trata", ou seja,
        que ele não tem nada o que fazer.
        Esse teste certifica que o join() não quebra em casos como esse
        """
        with application.test_request_context(
            "/v2/apps/myapp/restart", method="POST"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps({"deploymentId": "myId"}),
                status=HTTPStatus.OK,
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            joined_response = response.join([])

            joined_response_data = json.loads(joined_response.data)
            self.assertEqual("myId", joined_response_data["deploymentId"])

    @with_json_fixture("single_full_app.json")
    def test_it_recreates_a_get_response_for_a_single_app(self, fixture):
        with application.test_request_context(
            "/v2/apps//foo", method="GET", data=b""
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps({"app": fixture}),
                status=HTTPStatus.OK,
                headers={},
            )
            response = Response(ctx.request, response)

        with patch.object(response, "marathon_client") as client:
            client.get_app.return_value = AsgardApp.from_json(deepcopy(fixture))
            apps = list(response.split())

            joined_response = response.join(apps)

            self.assertIsInstance(joined_response, FlaskResponse)
            self.assertDictEqual(
                json.loads(joined_response.data), {"app": fixture}
            )

    @with_json_fixture("single_full_app.json")
    def test_it_recreates_a_get_response_for_multiple_apps(self, fixture):
        modified_app = deepcopy(fixture)
        modified_app["id"] = "/xablau"

        fixtures = [fixture, modified_app]
        expected_response = deepcopy(fixtures)
        with application.test_request_context(
            "/v2/apps/", method="GET", data=b""
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps({"apps": fixtures}),
                status=HTTPStatus.OK,
                headers={},
            )
            response = Response(ctx.request, response)

        with patch.object(response, "marathon_client") as client:
            original_apps = [AsgardApp.from_json(app) for app in fixtures]
            client.get_app.side_effect = original_apps
            apps = list(response.split())

            joined_response = response.join(apps)

            self.assertIsInstance(joined_response, FlaskResponse)
            self.assertDictEqual(
                json.loads(joined_response.data), {"apps": expected_response}
            )

    @with_json_fixture("single_full_app.json")
    def test_should_join_an_empty_list_into_an_empty_response_single_app(
        self, single_full_app_fixture
    ):
        with application.test_request_context(
            "/v2/apps//foo", method="GET", data=b""
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps({"app": single_full_app_fixture}),
                status=HTTPStatus.OK,
                headers={},
            )
            response = Response(ctx.request, response)

            joined_response = response.join([])

            self.assertIsInstance(joined_response, FlaskResponse)
            self.assertDictEqual(json.loads(joined_response.data), {"app": {}})

    @with_json_fixture("single_full_app.json")
    def test_should_join_an_empty_list_into_an_empty_response_multi_app(
        self, single_full_app_fixture
    ):
        modified_app = deepcopy(single_full_app_fixture)
        modified_app["id"] = "/other-app"

        fixtures = [single_full_app_fixture, modified_app]
        expected_response = deepcopy(fixtures)
        with application.test_request_context(
            "/v2/apps/", method="GET", data=b""
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps({"apps": fixtures}),
                status=HTTPStatus.OK,
                headers={},
            )
            response = Response(ctx.request, response)

            joined_response = response.join([])

            self.assertIsInstance(joined_response, FlaskResponse)
            self.assertDictEqual(json.loads(joined_response.data), {"apps": []})

    @with_json_fixture("../fixtures/group_dev_namespace_with_one_full_app.json")
    def test_join_groups(self, group_dev_namespace_fixture):
        with application.test_request_context(
            "/v2/groups/", method="GET"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture),
                status=HTTPStatus.OK,
                headers={},
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            groups_tuple = list(response.split())
            joined_response = response.join(groups_tuple)

            joined_response_data = json.loads(joined_response.data)
            self.assertEqual("/dev", joined_response_data["id"])
            self.assertEqual(
                "/dev/group-b", joined_response_data["groups"][0]["id"]
            )
            self.assertEqual(
                [], joined_response_data["dependencies"]
            )  # Groups should be reendered in full
            self.assertEqual(1, len(joined_response_data["groups"][0]["apps"]))
            self.assertEqual(
                [], joined_response_data["groups"][0]["apps"][0]["constraints"]
            )  # Apps should also be renderen in full

    @with_json_fixture("../fixtures/tasks/get_single_namespace.json")
    def test_join_tasks_GET(self, tasks_single_namespace_fixture):
        with application.test_request_context(
            "/v2/tasks/", method="GET"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps(tasks_single_namespace_fixture),
                status=HTTPStatus.OK,
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            tasks_tuple = list(response.split())
            joined_response = response.join(tasks_tuple)

            joined_response_data = json.loads(joined_response.data)
            self.assertEqual(3, len(joined_response_data["tasks"]))

    def test_join_tasks_empty_list_GET(self):
        """
        Se o request for GET e a lista de tasks for vazia, significa que todas as tasks
        foram removidas do response, isso significa que temos que retornar um response vazio.
        """
        with application.test_request_context(
            "/v2/tasks/", method="GET"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps({"tasks": [{"id": "some-filtered-task"}]}),
                status=HTTPStatus.OK,
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            joined_response = response.join([])

            joined_response_data = json.loads(joined_response.data)
            self.assertEqual(0, len(joined_response_data["tasks"]))

    @with_json_fixture("../fixtures/tasks/post?scale=true.json")
    def test_join_tasks_POST_scale_true(self, tasks_post_fixture):
        with application.test_request_context(
            "/v2/tasks/delete?scale=true", method="POST"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps(tasks_post_fixture), status=HTTPStatus.OK
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            tasks_tuple = list(response.split())
            joined_response = response.join(tasks_tuple)

            joined_response_data = json.loads(joined_response.data)
            self.assertEqual(
                "5ed4c0c5-9ff8-4a6f-a0cd-f57f59a34b43",
                joined_response_data["deploymentId"],
            )

    @with_json_fixture("../fixtures/tasks/get.json")
    def test_join_tasks_POST_scale_false(self, tasks_get_fixture):
        with application.test_request_context(
            "/v2/tasks/delete?scale=false", method="POST"
        ) as ctx:
            response = FlaskResponse(
                response=json.dumps(tasks_get_fixture), status=HTTPStatus.OK
            )

            ctx.request.user = self.user
            response = Response(ctx.request, response)
            tasks_tuple = list(response.split())
            joined_response = response.join(tasks_tuple)

            joined_response_data = json.loads(joined_response.data)
            self.assertEqual(3, len(joined_response_data["tasks"]))
