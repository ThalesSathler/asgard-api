import jwt

from asgard.api import accounts
from asgard.app import app
from asgard.http.auth.jwt import jwt_encode
from asgard.models.account import Account
from asgard.models.user import User
from hollowman.conf import SECRET_KEY
from itests.util import (
    BaseTestCase,
    USER_WITH_ONE_ACCOUNT_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_DICT,
    ACCOUNT_INFRA_ID,
    ACCOUNT_WITH_NO_USERS_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY,
)


class AccountsApiTest(BaseTestCase):
    async def setUp(self):
        await super(AccountsApiTest, self).setUp()
        self.client = await self.aiohttp_client(app)

    async def tearDown(self):
        await super(AccountsApiTest, self).tearDown()

    async def test_change_account_no_permission(self):
        jwt_token = jwt_encode(
            User(**USER_WITH_ONE_ACCOUNT_DICT), Account(**ACCOUNT_DEV_DICT)
        )
        resp = await self.client.get(
            f"/accounts/{ACCOUNT_INFRA_ID}/auth",
            headers={"Authorization": f"JWT {jwt_token.decode('utf-8')}"},
        )
        self.assertEqual(403, resp.status)

    async def test_change_account_does_not_exist(self):
        jwt_token = jwt_encode(
            User(**USER_WITH_ONE_ACCOUNT_DICT), Account(**ACCOUNT_DEV_DICT)
        )
        resp = await self.client.get(
            f"/accounts/8000/auth",
            headers={"Authorization": f"JWT {jwt_token.decode('utf-8')}"},
        )
        self.assertEqual(403, resp.status)

    async def test_account_permission_ok(self):
        jwt_token = jwt_encode(
            User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT),
            Account(**ACCOUNT_DEV_DICT),
        )
        resp = await self.client.get(
            f"/accounts/{ACCOUNT_INFRA_ID}/auth",
            headers={"Authorization": f"JWT {jwt_token.decode('utf-8')}"},
        )
        self.assertEqual(200, resp.status)
        data = await resp.json()
        returned_token = jwt.decode(data["jwt"], key=SECRET_KEY)
        self.assertDictEqual(
            User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT).dict(),
            returned_token["user"],
        )
        self.assertDictEqual(
            Account(**ACCOUNT_INFRA_DICT).dict(),
            returned_token["current_account"],
        )

    async def test_accounts_list_all(self):
        resp = await self.client.get(
            f"/accounts",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(200, resp.status)
        data = await resp.json()
        dev_account = Account(**ACCOUNT_DEV_DICT)
        self.assertEqual(
            {
                "accounts": [
                    Account(**ACCOUNT_DEV_DICT).dict(),
                    Account(**ACCOUNT_INFRA_DICT).dict(),
                    Account(**ACCOUNT_WITH_NO_USERS_DICT).dict(),
                ]
            },
            data,
        )
