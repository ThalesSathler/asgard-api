from asgard.db import AsgardDBSession
from asgard.models.account import Account
from asgard.models.user import User
from itests.util import (
    BaseTestCase,
    ACCOUNT_DEV_ID,
    ACCOUNT_DEV_NAME,
    ACCOUNT_DEV_NAMESPACE,
    ACCOUNT_DEV_OWNER,
    USER_WITH_NO_ACCOUNTS_DICT,
    ACCOUNT_DEV_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
)


class AccountModelTest(BaseTestCase):
    async def setUp(self):
        await super(AccountModelTest, self).setUp()

    async def tearDown(self):
        await super(AccountModelTest, self).tearDown()

    async def test_transform_from_alchemy_object(self):
        account = Account(**ACCOUNT_DEV_DICT)
        _, AccountTable = await account.to_alchemy_obj()
        async with AsgardDBSession() as s:
            account_db = (
                await s.query(AccountTable)
                .filter(AccountTable.id == ACCOUNT_DEV_ID)
                .one()
            )
            account = await Account.from_alchemy_obj(account_db)
            self.assertEqual(account.id, ACCOUNT_DEV_ID)
            self.assertEqual(account.name, ACCOUNT_DEV_NAME)
            self.assertEqual(account.namespace, ACCOUNT_DEV_NAMESPACE)
            self.assertEqual(account.owner, ACCOUNT_DEV_OWNER)

    async def test_trasnform_to_alchemy_object(self):
        account = Account(**ACCOUNT_DEV_DICT)
        _, AccountTable = await account.to_alchemy_obj()
        async with AsgardDBSession() as s:
            account_db = (
                await s.query(AccountTable)
                .filter(AccountTable.id == ACCOUNT_DEV_ID)
                .one()
            )
            account = await Account.from_alchemy_obj(account_db)
            self.assertEqual(account.id, ACCOUNT_DEV_ID)
            self.assertEqual(account.name, ACCOUNT_DEV_NAME)
            self.assertEqual(account.namespace, ACCOUNT_DEV_NAMESPACE)
            self.assertEqual(account.owner, ACCOUNT_DEV_OWNER)

    async def test_user_has_permission_permission_denied(self):
        """
        Dado um objeto User e um objeto Account,
        account.user_has_permission(user) retorna True/False se o usuário tem ou
        não permissão para acessar essa conta.
        """
        user = User(**USER_WITH_NO_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        self.assertFalse(await account.user_has_permission(user))

    async def test_user_has_permission_permission_ok(self):
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        self.assertTrue(await account.user_has_permission(user))
