from http import HTTPStatus

from asynctest.mock import ANY

from asgard.api import users
from asgard.api.resources import ErrorDetail, ErrorResource
from asgard.api.resources.users import (
    UserListResource,
    UserResource,
    UserAccountsResource,
)
from asgard.app import app
from asgard.http.auth.jwt import jwt_encode
from asgard.models.account import Account
from asgard.models.user import User
from itests.util import (
    BaseTestCase,
    USER_WITH_NO_ACCOUNTS_AUTH_KEY,
    USER_WITH_NO_ACCOUNTS_ID,
    USER_WITH_NO_ACCOUNTS_EMAIL,
    USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY,
    USER_WITH_ONE_ACCOUNT_AUTH_KEY,
    USER_WITH_MULTIPLE_ACCOUNTS_NAME,
    USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_ID,
    USER_WITH_NO_ACCOUNTS_DICT,
    USER_WITH_ONE_ACCOUNT_DICT,
    ACCOUNT_DEV_ID,
    ACCOUNT_DEV_NAME,
    ACCOUNT_DEV_NAMESPACE,
    ACCOUNT_DEV_OWNER,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_NAME,
    ACCOUNT_INFRA_NAMESPACE,
    ACCOUNT_INFRA_OWNER,
    ACCOUNT_INFRA_DICT,
)


class UsersTestCase(BaseTestCase):
    async def setUp(self):
        await super(UsersTestCase, self).setUp()
        self.client = await self.aiohttp_client(app)

    async def tearDown(self):
        await super(UsersTestCase, self).tearDown()

    async def test_returns_user_basic_info(self):

        resp = await self.client.get(
            "/users/me",
            headers={
                "Authorization": f"Token {USER_WITH_NO_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(401, resp.status)

    async def test_users_me_invalid_token(self):

        resp = await self.client.get(
            "/users/me", headers={"Authorization": f"Token Invalid-Token"}
        )
        self.assertEqual(401, resp.status)

    async def test_jwt_me_returns_user_info_with_alternate_accounts(self):
        """
        Conferir que a lista de contas alternativas, *não inclui* a conta atual,
        que está no token JWT
        """
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        jwt_token = jwt_encode(user, account)
        resp = await self.client.get(
            "/users/me",
            headers={"Authorization": f"JWT {jwt_token.decode('utf-8')}"},
        )
        self.assertEqual(200, resp.status)
        data = await resp.json()
        self.assertDictEqual(
            {
                "user": {
                    "name": USER_WITH_MULTIPLE_ACCOUNTS_NAME,
                    "email": USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
                    "id": USER_WITH_MULTIPLE_ACCOUNTS_ID,
                    "type": "ASGARD",
                },
                "current_account": {
                    "id": ACCOUNT_DEV_ID,
                    "type": "ASGARD",
                    "name": ACCOUNT_DEV_NAME,
                    "namespace": ACCOUNT_DEV_NAMESPACE,
                    "owner": ACCOUNT_DEV_OWNER,
                },
                "accounts": [
                    {
                        "id": 11,
                        "type": "ASGARD",
                        "name": ACCOUNT_INFRA_NAME,
                        "namespace": ACCOUNT_INFRA_NAMESPACE,
                        "owner": ACCOUNT_INFRA_OWNER,
                    }
                ],
            },
            data,
        )

    async def test_returns_user_info_no_permission_for_chosen_account(self):
        """
        Se fazemos um request GET /users/me?account_id=3
        mas o usuário não tem permissão para acessar a conta escolhida,
        devemos retornar HTTP 403
        """
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(id=99, name="", namespace="", owner="")
        jwt_token = jwt_encode(user, account)
        resp = await self.client.get(
            "/users/me",
            headers={"Authorization": f"JWT {jwt_token.decode('utf-8')}"},
        )
        self.assertEqual(401, resp.status)

    async def test_users_endpoint_list_users(self):
        resp = await self.client.get(
            "/users",
            headers={
                "Authorization": f"Token {USER_WITH_ONE_ACCOUNT_AUTH_KEY}"
            },
        )
        users_data = await resp.json()
        self.assertCountEqual(
            UserListResource(
                users=[
                    User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT),
                    User(**USER_WITH_NO_ACCOUNTS_DICT),
                    User(**USER_WITH_ONE_ACCOUNT_DICT),
                ]
            ).dict(),
            users_data,
        )

    async def test_get_user_by_id_user_exists(self):
        resp = await self.client.get(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(200, resp.status)
        user_data = await resp.json()
        self.assertEqual(
            UserResource(user=User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)),
            user_data,
        )

    async def test_get_user_by_id_user_not_found(self):
        resp = await self.client.get(
            f"/users/99",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(404, resp.status)
        user_data = await resp.json()
        self.assertEqual(UserResource(), user_data)

    async def test_create_user_all_OK(self):
        user = User(name="New User", email="newuser@server.com")
        resp = await self.client.post(
            f"/users",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=user.dict(),
        )
        self.assertEqual(201, resp.status)
        user_data = await resp.json()

        expected_result = UserResource(user=user).dict()
        expected_result["user"]["id"] = ANY
        self.assertEqual(expected_result, user_data)

    async def test_create_user_invalid_input(self):
        user = User(name="New User", email=USER_WITH_MULTIPLE_ACCOUNTS_EMAIL)
        resp = await self.client.post(
            f"/users",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            data="{data",
        )
        self.assertEqual(400, resp.status)

    async def test_create_user_duplicate_email(self):
        user = User(name="New User", email=USER_WITH_MULTIPLE_ACCOUNTS_EMAIL)
        resp = await self.client.post(
            f"/users",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=user.dict(),
        )
        self.assertEqual(422, resp.status)
        resp_data = await resp.json()
        expected_error_message = """ERROR:  duplicate key value violates unique constraint "user_tx_email_key"\nDETAIL:  Key (tx_email)=(john@host.com) already exists.\n"""
        self.assertEqual(
            ErrorResource(
                errors=[ErrorDetail(msg=expected_error_message)]
            ).dict(),
            resp_data,
        )

    async def test_get_accounts_from_user_user_with_accounts(self):
        resp = await self.client.get(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}/accounts",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(200, resp.status)
        accounts_data = await resp.json()
        self.assertEqual(
            UserAccountsResource(
                accounts=[
                    Account(**ACCOUNT_DEV_DICT),
                    Account(**ACCOUNT_INFRA_DICT),
                ]
            ).dict(),
            accounts_data,
        )

    async def test_get_accounts_from_user_user_not_found(self):
        resp = await self.client.get(
            f"/users/99/accounts",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(404, resp.status)
        accounts_data = await resp.json()
        self.assertEqual(UserAccountsResource().dict(), accounts_data)

    async def test_delete_user_user_with_no_accounts(self):
        resp = await self.client.delete(
            f"/users/{USER_WITH_NO_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(200, resp.status)
        resp_data = await resp.json()
        self.assertEqual(
            UserResource(user=User(**USER_WITH_NO_ACCOUNTS_DICT)).dict(),
            resp_data,
        )
        other_users = await self.client.get(
            f"/users",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        other_users_data = await other_users.json()
        self.assertCountEqual(
            UserListResource(
                users=[
                    User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT),
                    User(**USER_WITH_ONE_ACCOUNT_DICT),
                ]
            ).dict(),
            other_users_data,
        )

    async def test_delete_user_user_with_accounts(self):
        resp = await self.client.delete(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(200, resp.status)
        resp_data = await resp.json()
        self.assertEqual(
            UserResource(user=User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)).dict(),
            resp_data,
        )
        other_users = await self.client.get(
            f"/users",
            headers={
                "Authorization": f"Token {USER_WITH_ONE_ACCOUNT_AUTH_KEY}"
            },
        )

        other_users_data = await other_users.json()
        self.assertCountEqual(
            UserListResource(
                users=[
                    User(**USER_WITH_NO_ACCOUNTS_DICT),
                    User(**USER_WITH_ONE_ACCOUNT_DICT),
                ]
            ).dict(),
            other_users_data,
        )

    async def test_delete_user_user_not_fount(self):
        resp = await self.client.delete(
            f"/users/99",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(404, resp.status)
        resp_data = await resp.json()
        self.assertEqual(UserResource().dict(), resp_data)

    async def test_update_user_auth_required(self):
        resp = await self.client.patch(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            json={"name": "Novo Nome"},
        )
        self.assertEqual(HTTPStatus.UNAUTHORIZED, resp.status)

    async def test_update_user_invalid_json(self):
        resp = await self.client.patch(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            data="{data",
        )
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, resp.status)
        resp_data = await resp.json()
        expected_error_msg = "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"
        self.assertEqual(
            ErrorResource(errors=[ErrorDetail(msg=expected_error_msg)]).dict(),
            resp_data,
        )

    async def test_update_user_update_only_name(self):
        expected_new_name = "Novo Nome"
        new_user_data = {"name": expected_new_name}

        resp = await self.client.patch(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=new_user_data,
        )
        self.assertEqual(HTTPStatus.ACCEPTED, resp.status)
        user_data = await resp.json()

        new_user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        new_user.name = expected_new_name
        self.assertEqual(UserResource(user=new_user).dict(), user_data)

        resp = await self.client.get(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        updated_user_data = await resp.json()
        self.assertEqual(UserResource(user=new_user).dict(), updated_user_data)

    async def test_update_user_cant_update_another_user(self):
        """
        Dado um request 
          PATCH /users/42
          {"id": 50, "name": "Nome", "email": "email"}

        Não podemos, no final das contas ter atualizado o user id=50. Temos que atualizar o user id=42
        """
        expected_new_name = "Novo Nome"
        expected_new_email = "novemail@server.com"

        new_user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        new_user.name = expected_new_name
        new_user.email = expected_new_email
        new_user.id = USER_WITH_NO_ACCOUNTS_ID

        resp = await self.client.patch(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=new_user.dict(),
        )
        self.assertEqual(HTTPStatus.ACCEPTED, resp.status)
        user_data = await resp.json()

        expected_returned_user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        expected_returned_user.name = expected_new_name
        expected_returned_user.email = expected_new_email
        self.assertEqual(
            UserResource(user=expected_returned_user).dict(), user_data
        )

        resp = await self.client.get(
            f"/users/{USER_WITH_NO_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        updated_user_data = await resp.json()
        self.assertEqual(
            UserResource(user=User(**USER_WITH_NO_ACCOUNTS_DICT)).dict(),
            updated_user_data,
        )

    async def test_update_user_update_all_fields(self):
        expected_new_name = "Novo Nome"
        expected_new_email = "newemail@server.com"

        new_user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        new_user.name = expected_new_name
        new_user.email = expected_new_email

        resp = await self.client.patch(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=new_user.dict(),
        )
        self.assertEqual(HTTPStatus.ACCEPTED, resp.status)
        user_data = await resp.json()

        self.assertEqual(UserResource(user=new_user).dict(), user_data)

        resp = await self.client.get(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        updated_user_data = await resp.json()
        self.assertEqual(UserResource(user=new_user).dict(), updated_user_data)

    async def test_update_user_duplicate_email(self):
        expected_new_email = USER_WITH_NO_ACCOUNTS_EMAIL
        new_user_data = {"email": expected_new_email}

        resp = await self.client.patch(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
            json=new_user_data,
        )
        self.assertEqual(HTTPStatus.ACCEPTED, resp.status)
        user_data = await resp.json()

        new_user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        new_user.name = expected_new_email
        expected_error_message = """ERROR:  duplicate key value violates unique constraint "user_tx_email_key"\nDETAIL:  Key (tx_email)=(user-no-accounts@host.com) already exists.\n"""
        self.assertEqual(
            ErrorResource(
                errors=[ErrorDetail(msg=expected_error_message)]
            ).dict(),
            user_data,
        )

        resp = await self.client.get(
            f"/users/{USER_WITH_MULTIPLE_ACCOUNTS_ID}",
            headers={
                "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
            },
        )
        updated_user_data = await resp.json()
        self.assertEqual(
            UserResource(user=User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)).dict(),
            updated_user_data,
        )
