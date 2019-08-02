from asynctest import TestCase, CoroutineMock

from asgard.models.account import Account
from asgard.models.user import User
from asgard.services.accounts import AccountsService
from itests.util import ACCOUNT_DEV_DICT, USER_WITH_NO_ACCOUNTS_DICT


class AccountServiceTest(TestCase):
    async def test_calls_backend_with_correct_parameters(self):
        backend = CoroutineMock(get_account_by_id=CoroutineMock())
        account_id = 42
        await AccountsService.get_account_by_id(account_id, backend)
        backend.get_account_by_id.assert_awaited_with(account_id)

    async def test_calls_backend_accounts_list(self):
        backend = CoroutineMock(get_accounts=CoroutineMock())
        await AccountsService.get_accounts(backend)
        backend.get_accounts.assert_awaited_with()

    async def test_calls_backend_get_users_from_acount(self):
        account = Account(**ACCOUNT_DEV_DICT)
        backend = CoroutineMock(get_users_from_account=CoroutineMock())
        await AccountsService.get_users_from_account(account, backend)
        backend.get_users_from_account.assert_awaited_with(account)

    async def test_calls_backend_with_right_parameters_add_user(self):
        account = Account(**ACCOUNT_DEV_DICT)
        user = User(**USER_WITH_NO_ACCOUNTS_DICT)
        backend = CoroutineMock(add_user=CoroutineMock())
        await AccountsService.add_user_to_account(user, account, backend)
        backend.add_user.assert_awaited_with(user, account)

    async def test_calls_backend_with_right_parameters_remove_user(self):
        account = Account(**ACCOUNT_DEV_DICT)
        user = User(**USER_WITH_NO_ACCOUNTS_DICT)
        backend = CoroutineMock(remove_user=CoroutineMock())
        await AccountsService.remove_user_from_account(user, account, backend)
        backend.remove_user.assert_awaited_with(user, account)
