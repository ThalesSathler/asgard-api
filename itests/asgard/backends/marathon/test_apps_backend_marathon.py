import asyncio
from datetime import datetime, timezone

from aioelasticsearch import Elasticsearch

from asgard.backends.base import Interval
from asgard.backends.marathon.impl import MarathonAppsBackend
from asgard.backends.mesos.models.app import MesosApp
from asgard.conf import settings
from asgard.models.account import Account
from asgard.models.app import AppStats
from asgard.models.user import User
from itests.util import (
    BaseTestCase,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    ACCOUNT_DEV_DICT,
)
from tests.utils import get_fixture


class MarathonAppsBackendTest(BaseTestCase):
    async def setUp(self):
        await super(MarathonAppsBackendTest, self).setUp()
        self.utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.INDEX_NAME = (
            f"asgard-app-stats-{self.utc_now.strftime('%Y-%m-%d-%H')}"
        )
        self.interval = Interval.ONE_HOUR

    async def tearDown(self):
        await self.esclient.indices.delete(
            index=self.INDEX_NAME, ignore=[400, 404]
        )
        await super(MarathonAppsBackendTest, self).tearDown()

    async def test_get_apps_stats_with_data(self):
        """
        Prepara um ElasticSearch com alguns dados e faz o cálculo
        agregado do uso de CPU e RAM
        """
        app_stats_datapoints = get_fixture(
            f"agents/ead07ffb-5a61-42c9-9386-21b680597e6c-S0/app_stats.json"
        )
        app = MesosApp(id="infra/asgard/api")

        await self._load_app_stats_into_storage(
            self.INDEX_NAME, self.utc_now, app_stats_datapoints
        )

        backend = MarathonAppsBackend()
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        async with Elasticsearch([settings.STATS_API_URL]) as es:
            raw = await es.search(index=self.INDEX_NAME)
            cpu_pcts = [
                hit["_source"]["cpu_pct"] for hit in raw["hits"]["hits"]
            ]
            mem_pcts = [
                hit["_source"]["mem_pct"] for hit in raw["hits"]["hits"]
            ]
            self.assertEqual(5, len(cpu_pcts))
            self.assertEqual(5, len(mem_pcts))

        app_stats = await backend.get_app_stats(
            app, self.interval, user, account
        )
        self.assertEqual(
            AppStats(cpu_pct="0.25", ram_pct="15.05", cpu_thr_pct="1.00"),
            app_stats,
        )

    async def test_get_apps_stats_no_data(self):
        """
        Prepara um ElasticSearch com alguns dados e faz o cálculo
        agregado do uso de CPU e RAM
        """
        app_stats_datapoints = get_fixture(
            f"agents/ead07ffb-5a61-42c9-9386-21b680597e6c-S0/app_stats.json"
        )
        app = MesosApp(id="infra/app-does-not-exist")

        await self._load_app_stats_into_storage(
            self.INDEX_NAME, self.utc_now, app_stats_datapoints
        )

        backend = MarathonAppsBackend()
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        app_stats = await backend.get_app_stats(
            app, self.interval, user, account
        )
        self.assertEqual(
            AppStats(cpu_pct="0", ram_pct="0", cpu_thr_pct="0"), app_stats
        )
