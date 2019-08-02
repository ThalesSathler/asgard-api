import asgard.services.users
from asgard.backends.users import UsersBackend
from asgard.exceptions import DuplicateEntity
from asgard.models.account import Account
from asgard.models.user import User
from itests.util import (
    BaseTestCase,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_ID,
    USER_WITH_ONE_ACCOUNT_DICT,
    USER_WITH_NO_ACCOUNTS_DICT,
    USER_WITH_ONE_ACCOUNT_ID,
    USER_WITH_NO_ACCOUNTS_EMAIL,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_DICT,
)


class UsersBackendTest(BaseTestCase):
    async def setUp(self):
        await super(UsersBackendTest, self).setUp()
        self.backend = UsersBackend()

    async def tearDown(self):
        await super(UsersBackendTest, self).tearDown()

    async def test_get_alternate_accounts_for_user(self):
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        current_account = Account(**ACCOUNT_DEV_DICT)
        accounts = await UsersBackend().get_alternate_accounts(
            user, current_account
        )
        self.assertEqual(1, len(accounts))
        self.assertEqual([Account(**ACCOUNT_INFRA_DICT)], accounts)

    async def test_get_alternate_accounts_user_has_only_one_account(self):
        """
        Quando um user tem acesso a apenas uma conta, esse método deve retornar uma lista vazia
        """
        user = User(**USER_WITH_ONE_ACCOUNT_DICT)
        current_account = Account(**ACCOUNT_DEV_DICT)
        accounts = await UsersBackend().get_alternate_accounts(
            user, current_account
        )
        self.assertEqual(0, len(accounts))
        self.assertEqual([], accounts)

    async def test_get_user_by_id_user_exists(self):
        user = await self.backend.get_user_by_id(USER_WITH_ONE_ACCOUNT_ID)
        self.assertIsNotNone(user)
        self.assertEqual(User(**USER_WITH_ONE_ACCOUNT_DICT), user)

    async def test_get_user_by_id_user_not_found(self):
        user = await self.backend.get_user_by_id(99)
        self.assertIsNone(user)

    async def test_get_all_users(self):
        users = await self.backend.get_users()
        self.assertCountEqual(
            [
                User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT),
                User(**USER_WITH_ONE_ACCOUNT_DICT),
                User(**USER_WITH_NO_ACCOUNTS_DICT),
            ],
            users,
        )

    async def test_create_user_OK(self):
        user_name = "New User"
        user_email = "newuser@server.com"
        user_created = await self.backend.create_user(
            User(name=user_name, email=user_email)
        )
        self.assertEqual(
            user_created, User(id=1, name=user_name, email=user_email)
        )

    async def test_create_user_duplicate_email(self):
        user_name = "New User"
        user_email = USER_WITH_NO_ACCOUNTS_EMAIL
        with self.assertRaises(DuplicateEntity):
            await self.backend.create_user(
                User(name=user_name, email=user_email)
            )

    async def test_get_accounts_from_user_user_has_accounts(self):
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        accounts = await self.backend.get_accounts_from_user(user)
        self.assertCountEqual(
            [Account(**ACCOUNT_DEV_DICT), Account(**ACCOUNT_INFRA_DICT)],
            accounts,
        )

    async def test_get_accounts_from_user_user_has_no_accounts(self):
        user = User(**USER_WITH_NO_ACCOUNTS_DICT)
        accounts = await self.backend.get_accounts_from_user(user)
        self.assertCountEqual([], accounts)

    async def test_delete_user_with_no_accounts(self):
        total_users = await self.backend.get_users()
        self.assertEqual(3, len(total_users))

        user = User(**USER_WITH_NO_ACCOUNTS_DICT)
        deleted_user = await self.backend.delete_user(user)
        self.assertEqual(deleted_user, user)

        remain_users = await self.backend.get_users()
        self.assertEqual(2, len(remain_users))
        self.assertCountEqual(
            [
                User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT),
                User(**USER_WITH_ONE_ACCOUNT_DICT),
            ],
            remain_users,
        )

    async def test_delete_user_with_accounts(self):
        total_users = await self.backend.get_users()
        self.assertEqual(3, len(total_users))

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        deleted_user = await self.backend.delete_user(user)
        self.assertEqual(deleted_user, user)

        remain_users = await self.backend.get_users()
        self.assertEqual(2, len(remain_users))
        self.assertCountEqual(
            [
                User(**USER_WITH_NO_ACCOUNTS_DICT),
                User(**USER_WITH_ONE_ACCOUNT_DICT),
            ],
            remain_users,
        )

    async def test_update_user_update_all_fields(self):
        expected_new_name = "Novo Nome"
        expected_new_email = "novo@server.com"
        new_user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        new_user.name = expected_new_name
        new_user.email = expected_new_email

        updated_user = await self.backend.update_user(new_user)
        self.assertEqual(new_user, updated_user)

        saved_user = await self.backend.get_user_by_id(
            USER_WITH_MULTIPLE_ACCOUNTS_ID
        )
        self.assertEqual(new_user, saved_user)

    async def test_update_user_update_name(self):
        expected_new_email = "novo@server.com"
        new_user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        new_user.email = expected_new_email

        updated_user = await self.backend.update_user(new_user)
        self.assertEqual(new_user, updated_user)

        saved_user = await self.backend.get_user_by_id(
            USER_WITH_MULTIPLE_ACCOUNTS_ID
        )
        self.assertEqual(new_user, saved_user)

    async def test_update_user_duplicate_email(self):
        expected_new_email = USER_WITH_NO_ACCOUNTS_EMAIL
        new_user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        new_user.email = expected_new_email

        with self.assertRaises(DuplicateEntity):
            updated_user = await self.backend.update_user(new_user)
