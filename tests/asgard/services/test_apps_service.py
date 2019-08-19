from asynctest import TestCase
from asynctest.mock import CoroutineMock

from asgard.backends.base import Orchestrator, Interval
from asgard.backends.mesos.impl import MesosOrchestrator
from asgard.backends.mesos.models.app import MesosApp
from asgard.models.account import Account
from asgard.models.user import User
from asgard.services.apps import AppsService
from itests.util import ACCOUNT_DEV_DICT, USER_WITH_MULTIPLE_ACCOUNTS_DICT


class AppsServiceTest(TestCase):
    async def setUp(self):
        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        self.account = Account(**ACCOUNT_DEV_DICT)

    async def test_calls_backend_with_correct_parameters(self):
        orchestrator = CoroutineMock(spec=Orchestrator)
        app_id = "infra/app/nodes"
        app = MesosApp(id=app_id)
        await AppsService.get_app_stats(
            app_id, Interval.ONE_HOUR, self.user, self.account, orchestrator
        )
        orchestrator.get_app_stats.assert_awaited_with(
            app, Interval.ONE_HOUR, self.user, self.account
        )
