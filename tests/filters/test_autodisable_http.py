import unittest
from unittest import skip

from asgard.models.account import AccountDB as Account
from hollowman.filters.autodisablehttp import AutoDisableHTTPFilter
from hollowman.marathonapp import AsgardApp
from hollowman.models import User
from tests.utils import with_json_fixture

APP_WITH_HTTP_LABELS = "single_full_app_with_http_labels.json"


class TestAutoDisableHTTPFilter(unittest.TestCase):
    @with_json_fixture(APP_WITH_HTTP_LABELS)
    def setUp(self, single_full_app_fixture):
        self.filter = AutoDisableHTTPFilter()
        self.request_app = AsgardApp.from_json(single_full_app_fixture)
        self.original_app = AsgardApp.from_json(single_full_app_fixture)
        self.account = Account(
            name="Dev Account", namespace="dev", owner="company"
        )
        self.user = User(tx_email="user@host.com.br")
        self.user.current_account = self.account

    def test_create_app_with_zero_instances(self):
        self.request_app.instances = 0
        self.assertTrue(self.request_app.labels["traefik.enable"])

        filtered_app = self.filter.write(
            self.user, self.request_app, AsgardApp()
        )

        self.assertEqual("false", filtered_app.labels["traefik.enable"])

    def test_should_not_modify_non_http_apps(self):
        self.request_app.instances = 0
        del self.request_app.labels["traefik.enable"]

        filtered_app = self.filter.write(
            self.user, self.request_app, AsgardApp()
        )

        self.assertTrue("traefik.enable" not in filtered_app.labels)

    def test_update_suspended_app_set_instances_to_zero(self):
        self.request_app = AsgardApp.from_json({"env": {"ENV_A": "VALUE"}})
        self.original_app.instances = 10

        filtered_app = self.filter.write(
            self.user, self.request_app, AsgardApp()
        )

        self.assertIsNone(filtered_app.labels.get("traefik.enable"))

    def test_update_running_app_set_instances_to_zero(self):
        self.original_app.instances = 10
        self.request_app.instances = 0

        self.assertTrue(self.request_app.labels["traefik.enable"])
        filtered_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )
        self.assertEqual("false", filtered_app.labels["traefik.enable"])

    def test_should_enable_http_when_scaling_from_zero_to_some(self):
        self.original_app.instances = 0
        self.request_app.instances = 7

        self.original_app.labels["traefik.enable"] = False
        self.request_app.labels["traefik.enable"] = False

        filtered_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )
        self.assertEqual("true", self.request_app.labels["traefik.enable"])

    def test_shouldnt_modify_app_if_instances_fields_is_not_present(self):
        self.request_app.instances = None
        self.original_app = AsgardApp()

        self.request_app.labels["traefik.enable"] = "true"

        self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual("true", self.request_app.labels["traefik.enable"])
