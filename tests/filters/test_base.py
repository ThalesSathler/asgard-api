#encoding: utf-8

from hollowman.filters import BaseFilter
from hollowman.filters import Context
from tests import RequestStub
import unittest

from marathon.models.app import MarathonApp
import mock


class BaseFilterTest(unittest.TestCase):

    def setUp(self):
        self.ctx = Context(marathon_client=None, request=None)
        self.filter = BaseFilter()

    def test_is_request_on_app(self):
        self.assertTrue(self.filter.is_request_on_app("/v2/apps//app/foo"))
        self.assertFalse(self.filter.is_request_on_app("/v2/apps/"))
        self.assertTrue(self.filter.is_request_on_app("/v2/apps//app/foo/versions"))
        self.assertFalse(self.filter.is_request_on_app("/v2/apps"))
        self.assertFalse(self.filter.is_request_on_app("/v2/groups"))

    def test_get_app_id(self):
        self.assertEqual('', self.filter.get_app_id('/v2/apps'))
        self.assertEqual('', self.filter.get_app_id('/v2/apps/'))

        self.assertEqual('/foo', self.filter.get_app_id('/v2/apps//foo'))
        self.assertEqual('/foo/taz/bar', self.filter.get_app_id('/v2/apps//foo/taz/bar'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/restart'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/restart/'))
        self.assertEqual('/foo/taz-restart', self.filter.get_app_id('/v2/apps//foo/taz-restart/versions/version-id'))

        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/tasks'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/tasks/'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/tasks/task-id'))
        self.assertEqual('/foo/taz-tasks', self.filter.get_app_id('/v2/apps//foo/taz-tasks/versions/version-id'))

        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/versions'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/versions/'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/versions/version-id'))
        self.assertEqual('/foo/taz-versions', self.filter.get_app_id('/v2/apps//foo/taz-versions/versions/version-id'))


    def test_is_docker_app(self):
        data_ = {
            "id": "/",
            "apps": [],
            "groups": []
        }
        self.assertFalse(self.filter.is_docker_app(data_))
        data_ = {
            "id": "/foo",
            "container": {
                "docker": {
                    "image": "alpine:3.4"
                }
            }
        }
        self.assertTrue(self.filter.is_docker_app(data_))

    def test_get_apps_from_groups(self):
        data_ = {"id": "/"}
        self.assertEqual([], self.filter.get_apps_from_group(data_))

        data_ = {
            "id": "/",
            "apps": [
                {},
                {},
                {},
            ]
        }
        self.assertEqual([{}, {}, {}], self.filter.get_apps_from_group(data_))

    def test_is_group(self):
        data_ = {
            "id": "/",
            "groups": [
                {
                  "id": "/bla"
                },
                {
                    "id": "/foo"
                }
            ]
        }
        self.assertTrue(self.filter.is_group(data_))
        data_ = {
            "id": "/abc",
            "container": {
                "docker": {
                }
            }
        }
        self.assertFalse(self.filter.is_group(data_))

    def test_is_single_app(self):
        data_ = {
            "id": "/daltonmatos/sleep2",
            "cmd": "sleep 40000",
            "cpus": 1,
            "mem": 128,
            "disk": 0,
            "instances": 0,
            "container": {
                  "type": "DOCKER",
                  "docker": {
                      "image": "alpine:3.4",
                      "network": "BRIDGE",
                  },
            }
        }
        self.assertTrue(self.filter.is_single_app(data_))
        data_ = {"id": "/foo", "apps": {}}
        self.assertFalse(self.filter.is_single_app(data_))
        data_ = {"id": "/foo", "groups": {}}
        self.assertFalse(self.filter.is_single_app(data_))

        data_ = [
            {"id": "/foo"},
            {"id": "/bar"}
        ]
        self.assertFalse(self.filter.is_single_app(data_))

    def test_is_multi_app(self):
        data_ = [
            {"id": "/foo"},
            {"id": "/bar"}
        ]
        self.assertTrue(self.filter.is_multi_app(data_))

    def test_get_original_app(self):
        """
        If app does not exist yet, return an empty marathon.models.app.MarathonApp()
        """
        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps", data={})
            ctx_mock.marathon_client.get_app.side_effect = KeyError()
            ctx_mock.request = request

            marathon_app = self.filter.get_original_app(ctx_mock)
            self.assertIsNone(marathon_app.id)
            self.assertIsNotNone(marathon_app)

    def test_empty_marathon_app_to_json(self):
        empty_app = MarathonApp()
        self.assertEqual('{}', empty_app.to_json())

    def test_default_instances_value_on_empty_app(self):
        empty_app = MarathonApp()
        self.assertEqual(None, empty_app.instances)

    def test_is_network_host_legit_app(self):
        data = {
            "id": "/foo/sleep2",
            "cmd": "sleep 40000",
            "cpus": 1,
            "mem": 128,
            "disk": 0,
            "instances": 0,
            "container": {
                  "type": "DOCKER",
                  "docker": {
                      "image": "alpine:3.4",
                      "network": "HOST",
                  },
            }
        }

        marathon_app = MarathonApp(**data)

        self.assertTrue(self.filter.is_app_network_host(marathon_app))

    def test_is_network_host_legit_app_bridge(self):
        data = {
            "id": "/foo/sleep2",
            "cmd": "sleep 40000",
            "cpus": 1,
            "mem": 128,
            "disk": 0,
            "instances": 0,
            "container": {
                  "type": "DOCKER",
                  "docker": {
                      "image": "alpine:3.4",
                      "network": "BRIDGE",
                  },
            }
        }

        marathon_app = MarathonApp(**data)

        self.assertFalse(self.filter.is_app_network_host(marathon_app))

    def test_is_network_host_incomplete_app(self):
        data = {
            "id": "/foo/sleep2",
            "disk": 0,
            "instances": 0
        }

        marathon_app = MarathonApp(**data)

        self.assertFalse(self.filter.is_app_network_host(marathon_app))

    def test_is_network_host_none_app(self):
        self.assertFalse(self.filter.is_app_network_host(MarathonApp()))


class TestContext(unittest.TestCase):

    def test_set_marathon_client(self):
        ctx = Context(marathon_client=True, request=None)
        self.assertTrue(ctx.marathon_client)

    def test_set_request(self):
        ctx = Context(marathon_client=None, request=True)
        self.assertTrue(ctx.request)
