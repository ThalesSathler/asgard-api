from typing import List, Optional

from asgard.backends.users import UsersBackend
from asgard.models.account import Account
from asgard.models.user import User


class UsersService:
    @staticmethod
    async def get_alternate_accounts(
        user: User, current_account: Account, backend: UsersBackend
    ) -> List[Account]:
        return await backend.get_alternate_accounts(user, current_account)

    @staticmethod
    async def get_user_by_id(
        user_id: int, backend: UsersBackend
    ) -> Optional[User]:
        return await backend.get_user_by_id(user_id)

    @staticmethod
    async def get_users(backend: UsersBackend) -> List[User]:
        return await backend.get_users()

    @staticmethod
    async def create_user(user: User, backend: UsersBackend) -> User:
        return await backend.create_user(user)

    @staticmethod
    async def get_accounts_from_user(
        user: User, backend: UsersBackend
    ) -> List[Account]:
        return await backend.get_accounts_from_user(user)

    @staticmethod
    async def delete_user(user: User, backend: UsersBackend) -> User:
        return await backend.delete_user(user)

    @staticmethod
    async def update_user(user: User, backend: UsersBackend) -> User:
        return await backend.update_user(user)
