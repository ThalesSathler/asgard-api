from asgard.backends.accounts import AccountsBackend
from asgard.models.account import Account
from itests.util import BaseTestCase, ACCOUNT_DEV_ID, ACCOUNT_DEV_DICT


class AccountsBackendTest(BaseTestCase):
    async def setUp(self):
        await super(AccountsBackendTest, self).setUp()
        self.backend = AccountsBackend()

    async def tearDown(self):
        await super(AccountsBackendTest, self).tearDown()

    async def test_get_account_by_id_account_not_found(self):
        account = await self.backend.get_account_by_id(8000)
        self.assertIsNone(account)

    async def test_account_by_id_account_exists(self):
        account = await self.backend.get_account_by_id(ACCOUNT_DEV_ID)
        self.assertEqual(Account(**ACCOUNT_DEV_DICT), account)

    async def test_account_list_all_accounts_empty_result(self):
        accounts = await self.backend.get_accounts()
        self.assertEquals(3, len(accounts))
