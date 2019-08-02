from typing import Optional, List

from asgard.backends.accounts import AccountsBackend
from asgard.models.account import Account
from asgard.models.user import User


class AccountsService:
    @staticmethod
    async def get_account_by_id(
        account_id: int, backend: AccountsBackend
    ) -> Optional[Account]:
        return await backend.get_account_by_id(account_id)

    @staticmethod
    async def get_accounts(backend: AccountsBackend) -> List[Account]:
        return await backend.get_accounts()

    @staticmethod
    async def get_users_from_account(
        account: Account, backend: AccountsBackend
    ) -> List[User]:
        return await backend.get_users_from_account(account)

    @staticmethod
    async def add_user_to_account(
        user: User, account: Account, backend: AccountsBackend
    ) -> None:
        return await backend.add_user(user, account)

    @staticmethod
    async def remove_user_from_account(
        user: User, account: Account, backend: AccountsBackend
    ) -> None:
        return await backend.remove_user(user, account)
