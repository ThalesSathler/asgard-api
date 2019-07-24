import asyncio
import os
import random
import string
from collections import defaultdict
from typing import Any, Dict, List, Type, Set

import asyncworker
from aioelasticsearch import Elasticsearch
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from aiopg.sa import Engine
from asynctest import TestCase
from sqlalchemy import Table
from sqlalchemy.sql.ddl import CreateTable

import asgard.backends.users
from asgard.conf import settings
from asgard.db import _SessionMaker
from asgard.http.client import http_client
from asgard.models.account import AccountDB as Account
from asgard.models.user import UserDB as User
from asgard.models.user_has_account import UserHasAccount


class PgDataMocker:
    def __init__(self, pool: Engine) -> None:
        self.data: Dict[Table, List[Dict]] = defaultdict(list)
        self.pool = pool
        self.schema = "".join(random.choices(string.ascii_lowercase, k=10))
        self._used_tables: List[Table] = []
        self._table_names: Set[str] = set()
        self._original_table_schemas: Dict[Table, str] = {}

    def add_data(
        self, model: Type, field_names: List[str], data: List[List[Any]]
    ):
        if not data:
            return
        assert all(len(field_names) == len(row) for row in data)

        if type(model) is not Table:
            table = model.__table__
        else:
            table = model

        if table.name not in self._table_names:
            # ensure schema
            self._original_table_schemas[table] = table.schema
            table.schema = self.schema
            self._used_tables.append(table)

        self.data[table].extend((dict(zip(field_names, row)) for row in data))
        self._table_names.add(table.name)

    async def _create_schema(self):
        await self._drop_schema_only()
        async with self.pool.acquire() as conn:
            await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")
            for table in self._used_tables:
                await conn.execute(CreateTable(table))

    async def create(self):
        await self._create_schema()
        commands = (
            table.insert().values(self.data[table])
            for table in self._used_tables
        )
        async with self.pool.acquire() as conn:
            for command in commands:
                await conn.execute(command)

    async def _drop_schema_only(self):
        async with self.pool.acquire() as conn:
            await conn.execute(f"DROP SCHEMA IF EXISTS {self.schema} CASCADE")

    async def drop(self):
        await self._drop_schema_only()
        for table, original_schema in self._original_table_schemas.items():
            table.schema = original_schema


ACCOUNT_INFRA_NAME: str = "Infra Team"
ACCOUNT_INFRA_ID: int = 11
ACCOUNT_INFRA_NAMESPACE: str = "infra"
ACCOUNT_INFRA_OWNER: str = "infra"


ACCOUNT_INFRA_DICT = {
    "id": ACCOUNT_INFRA_ID,
    "name": ACCOUNT_INFRA_NAME,
    "namespace": ACCOUNT_INFRA_NAMESPACE,
    "owner": ACCOUNT_INFRA_OWNER,
}

ACCOUNT_DEV_NAME: str = "Dev Team"
ACCOUNT_DEV_ID: int = 10
ACCOUNT_DEV_NAMESPACE: str = "dev"
ACCOUNT_DEV_OWNER: str = "dev"

ACCOUNT_DEV_DICT = {
    "id": ACCOUNT_DEV_ID,
    "name": ACCOUNT_DEV_NAME,
    "namespace": ACCOUNT_DEV_NAMESPACE,
    "owner": ACCOUNT_DEV_OWNER,
}


ACCOUNT_WITH_NO_USERS_ID = 12
ACCOUNT_WITH_NO_USERS_NAME = "Other Team"
ACCOUNT_WITH_NO_USERS_NAMESPACE = "other"
ACCOUNT_WITH_NO_USERS_OWNER = "other"
ACCOUNT_WITH_NO_USERS_DICT = {
    "id": ACCOUNT_WITH_NO_USERS_ID,
    "name": ACCOUNT_WITH_NO_USERS_NAME,
    "namespace": ACCOUNT_WITH_NO_USERS_NAMESPACE,
    "owner": ACCOUNT_WITH_NO_USERS_OWNER,
}


USER_WITH_ONE_ACCOUNT_ID = 22
USER_WITH_ONE_ACCOUNT_AUTH_KEY = "7259c8ce82294480b1be60835b74de0c"
USER_WITH_ONE_ACCOUNT_NAME = "User one account"
USER_WITH_ONE_ACCOUNT_EMAIL = "userone@server.com"

USER_WITH_ONE_ACCOUNT_DICT = {
    "id": USER_WITH_ONE_ACCOUNT_ID,
    "name": USER_WITH_ONE_ACCOUNT_NAME,
    "email": USER_WITH_ONE_ACCOUNT_EMAIL,
}

USER_WITH_NO_ACCOUNTS_ID = 21
USER_WITH_NO_ACCOUNTS_AUTH_KEY = "7b4184bfe7d2349eb56bcfb9dc246cf8"
USER_WITH_NO_ACCOUNTS_NAME = "User with no acounts"
USER_WITH_NO_ACCOUNTS_EMAIL = "user-no-accounts@host.com"

USER_WITH_NO_ACCOUNTS_DICT = {
    "id": USER_WITH_NO_ACCOUNTS_ID,
    "name": USER_WITH_NO_ACCOUNTS_NAME,
    "email": USER_WITH_NO_ACCOUNTS_EMAIL,
}

USER_WITH_MULTIPLE_ACCOUNTS_ID = 20
USER_WITH_MULTIPLE_ACCOUNTS_EMAIL = "john@host.com"
USER_WITH_MULTIPLE_ACCOUNTS_NAME = "John Doe"
USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY = "69ed620926be4067a36402c3f7e9ddf0"


USER_WITH_MULTIPLE_ACCOUNTS_DICT = {
    "id": USER_WITH_MULTIPLE_ACCOUNTS_ID,
    "name": USER_WITH_MULTIPLE_ACCOUNTS_NAME,
    "email": USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
}


_session = None
_pool = None


class BaseTestCase(TestCase):
    use_default_loop = True

    async def conn_pool(self):
        global _session, _pool
        if not _session:
            _session = _SessionMaker(settings.DB_URL)
            _pool = await _session.engine()

        return _pool

    async def setUp(self):

        self.esclient = Elasticsearch([settings.STATS_API_URL])
        self.pg_data_mocker = PgDataMocker(pool=await self.conn_pool())
        self.users_fixture = [
            [
                USER_WITH_MULTIPLE_ACCOUNTS_ID,
                USER_WITH_MULTIPLE_ACCOUNTS_NAME,
                USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
                USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY,
            ],
            [
                USER_WITH_NO_ACCOUNTS_ID,
                USER_WITH_NO_ACCOUNTS_NAME,
                USER_WITH_NO_ACCOUNTS_EMAIL,
                USER_WITH_NO_ACCOUNTS_AUTH_KEY,
            ],
            [
                USER_WITH_ONE_ACCOUNT_ID,
                USER_WITH_ONE_ACCOUNT_NAME,
                USER_WITH_ONE_ACCOUNT_EMAIL,
                USER_WITH_ONE_ACCOUNT_AUTH_KEY,
            ],
        ]
        self.pg_data_mocker.add_data(
            User,
            ["id", "tx_name", "tx_email", "tx_authkey"],
            self.users_fixture,
        )

        self.pg_data_mocker.add_data(
            Account,
            ["id", "name", "namespace", "owner"],
            [
                [
                    ACCOUNT_DEV_ID,
                    ACCOUNT_DEV_NAME,
                    ACCOUNT_DEV_NAMESPACE,
                    ACCOUNT_DEV_OWNER,
                ],
                [
                    ACCOUNT_INFRA_ID,
                    ACCOUNT_INFRA_NAME,
                    ACCOUNT_INFRA_NAMESPACE,
                    ACCOUNT_INFRA_OWNER,
                ],
                [
                    ACCOUNT_WITH_NO_USERS_ID,
                    ACCOUNT_WITH_NO_USERS_NAME,
                    ACCOUNT_WITH_NO_USERS_NAMESPACE,
                    ACCOUNT_WITH_NO_USERS_OWNER,
                ],
            ],
        )

        self.pg_data_mocker.add_data(
            UserHasAccount,
            ["id", "user_id", "account_id"],
            [
                [10, USER_WITH_MULTIPLE_ACCOUNTS_ID, ACCOUNT_DEV_ID],
                [11, USER_WITH_MULTIPLE_ACCOUNTS_ID, ACCOUNT_INFRA_ID],
                [12, USER_WITH_ONE_ACCOUNT_ID, ACCOUNT_DEV_ID],
            ],  # John Doe, accounts: Dev Team, Infra Team
        )
        await self.pg_data_mocker.create()

    async def tearDown(self):
        await self.pg_data_mocker.drop()
        if hasattr(self, "server"):
            await self.server.close()

    async def aiohttp_client(self, app: asyncworker.App) -> TestClient:
        routes = app.routes_registry.http_routes
        http_app = web.Application()
        for route in routes:
            http_app.router.add_route(**route)
        self.server = TestServer(
            http_app, port=os.environ["TEST_ASYNCWORKER_HTTP_PORT"]
        )
        client = TestClient(self.server)
        await self.server.start_server()

        return client

    async def _load_app_stats_into_storage(
        self, index_name, timestamp_to_use, datapoints
    ):
        """
        Carrega no elasticsearch local os datapoints de estatísticas de apps
        O `timestamp` usado em cada datapoint é o `timestamp_to_use`.
        """
        for datapoint in datapoints:
            datapoint["timestamp"] = timestamp_to_use.isoformat()
            await self.esclient.index(
                index=index_name, doc_type="stats", body=datapoint
            )
        # para dar tempo do Elasticsearch local indexar os dados recém inseridos
        await asyncio.sleep(3)


async def _load_jobs_into_chronos(jobs_list):
    base_url = f"{settings.SCHEDULED_JOBS_SERVICE_ADDRESS}/v1/scheduler"
    async with http_client as http:
        all_jobs = await http.get(f"{base_url}/jobs")
        all_jobs_json = await all_jobs.json()
        [
            await http.delete(f"{base_url}/job/{job['name']}")
            for job in all_jobs_json
        ]

        for job in jobs_list:
            await http.post(f"{base_url}/iso8601", json=job)

    await asyncio.sleep(1)
