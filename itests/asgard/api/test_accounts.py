import jwt

from asgard.api import accounts
from asgard.api.resources.accounts import AccountResource
from asgard.app import app
from asgard.http.auth.jwt import jwt_encode
from asgard.models.account import Account
from asgard.models.user import User
from hollowman.conf import SECRET_KEY
from itests.util import (
    BaseTestCase,
    USER_WITH_ONE_ACCOUNT_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_ID,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_DICT,
    ACCOUNT_INFRA_ID,
    ACCOUNT_WITH_NO_USERS_DICT,
    ACCOUNT_WITH_NO_USERS_ID,
    USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY,
    USER_WITH_NO_ACCOUNTS_ID,
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

    async def test_accounts_get_by_id_account_exists(self):
        resp = await self.client.get(
            f"/accounts/{ACCOUNT_INFRA_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(200, resp.status)
        data = await resp.json()
        self.assertEqual(
            {"account": Account(**ACCOUNT_INFRA_DICT).dict()}, data
        )

    async def test_accounts_get_by_id_account_not_found(self):
        resp = await self.client.get(
            f"/accounts/42",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(404, resp.status)
        data = await resp.json()
        self.assertEqual(AccountResource(), data)

    async def test_accounts_get_users_account_does_not_exist(self):
        resp = await self.client.get(
            f"/accounts/42/users",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(404, resp.status)
        data = await resp.json()
        self.assertEqual({"users": []}, data)

    async def test_accounts_get_users_account_has_users(self):
        resp = await self.client.get(
            f"/accounts/{ACCOUNT_INFRA_ID}/users",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(200, resp.status)
        data = await resp.json()
        self.assertEqual(
            {"users": [User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)]}, data
        )

    async def test_accounts_get_users_account_does_not_have_any_users(self):
        resp = await self.client.get(
            f"/accounts/{ACCOUNT_WITH_NO_USERS_ID}/users",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(200, resp.status)
        data = await resp.json()
        self.assertEqual({"users": []}, data)

    async def test_accounts_add_users_to_account_input_OK(self):
        """
        Quando o body do request é válido, vinculamos o novo user à conta
        """
        resp = await self.client.post(
            f"/accounts/{ACCOUNT_WITH_NO_USERS_ID}/users/{USER_WITH_NO_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(200, resp.status)
        data = await resp.json()
        self.assertEqual({"users": []}, data)

        resp_check = await self.client.get(
            f"/accounts/{ACCOUNT_WITH_NO_USERS_ID}/users",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        resp_check_data = await resp_check.json()
        users_ids = [User(**u).id for u in resp_check_data["users"]]
        self.assertIn(USER_WITH_NO_ACCOUNTS_ID, users_ids)

    async def test_account_add_user_account_not_found(self):
        resp = await self.client.post(
            f"/accounts/99/users/{USER_WITH_NO_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(404, resp.status)
        data = await resp.json()
        self.assertEqual({"users": []}, data)

    async def test_account_add_user_user_not_found(self):
        resp = await self.client.post(
            f"/accounts/99/users/99",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(404, resp.status)
        data = await resp.json()
        self.assertEqual({"users": []}, data)

    async def test_accounts_remove_user_user_in_account(self):
        """
        Quando o body do request é válido, removemos o user da conta
        """
        resp = await self.client.delete(
            f"/accounts/{ACCOUNT_INFRA_ID}/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(200, resp.status)
        data = await resp.json()
        self.assertEqual({"users": []}, data)

        resp_check = await self.client.get(
            f"/accounts/{ACCOUNT_INFRA_ID}/users",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        resp_check_data = await resp_check.json()
        users_ids = [User(**u).id for u in resp_check_data["users"]]
        self.assertNotIn(USER_WITH_NO_ACCOUNTS_ID, users_ids)

    async def test_account_remove_user_account_not_found(self):
        resp = await self.client.delete(
            f"/accounts/99/users/{USER_WITH_NO_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(404, resp.status)
        data = await resp.json()
        self.assertEqual({"users": []}, data)

    async def test_account_remove_user_user_not_found(self):
        resp = await self.client.delete(
            f"/accounts/99/users/99",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json={},
        )
        self.assertEqual(404, resp.status)
        data = await resp.json()
        self.assertEqual({"users": []}, data)

    async def test_account_remove_user_input_not_in_account(self):
        resp = await self.client.delete(
            f"/accounts/{ACCOUNT_WITH_NO_USERS_ID}/users/{USER_WITH_NO_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json={"id": USER_WITH_NO_ACCOUNTS_ID},
        )
        self.assertEqual(200, resp.status)
        data = await resp.json()
        self.assertEqual({"users": []}, data)

        resp_check = await self.client.get(
            f"/accounts/{ACCOUNT_WITH_NO_USERS_ID}/users",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        resp_check_data = await resp_check.json()
        users_ids = [User(**u).id for u in resp_check_data["users"]]
        self.assertNotIn(USER_WITH_NO_ACCOUNTS_ID, users_ids)
