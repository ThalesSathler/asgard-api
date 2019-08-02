from asynctest import TestCase
from asynctest.mock import CoroutineMock

from asgard.backends.users import UsersBackend
from asgard.services.users import UsersService


class UsersServiceTest(TestCase):
    async def setUp(self):
        self.service = UsersService()

    async def test_calls_get_alternate_accounts(self):
        backend = CoroutineMock(get_alternate_accounts=CoroutineMock())
        user = CoroutineMock()
        current_account = CoroutineMock()
        await UsersService.get_alternate_accounts(
            user, current_account, backend
        )
        backend.get_alternate_accounts.assert_awaited_with(
            user, current_account
        )

    async def test_calls_backend_get_user_by_id(self):
        backend = CoroutineMock(get_user_by_id=CoroutineMock())
        await self.service.get_user_by_id(42, backend)
        backend.get_user_by_id.assert_awaited_with(42)

    async def test_calls_backend_get_users(self):
        backend = CoroutineMock(get_users=CoroutineMock())
        await self.service.get_users(backend)
        backend.get_users.assert_awaited_with()

    async def test_calls_backend_create_user(self):
        user = CoroutineMock()
        backend = CoroutineMock(create_user=CoroutineMock())
        await self.service.create_user(user, backend)
        backend.create_user.assert_awaited_with(user)

    async def test_calls_backend_get_accounts_from_user(self):
        user = CoroutineMock()
        backend = CoroutineMock(spec=UsersBackend)
        await self.service.get_accounts_from_user(user, backend)
        backend.get_accounts_from_user.assert_awaited_with(user)

    async def test_calls_backend_delete_user(self):
        user = CoroutineMock()
        backend = CoroutineMock(spec=UsersBackend)
        await self.service.delete_user(user, backend)
        backend.delete_user.assert_awaited_with(user)

    async def test_calls_backend_update_user(self):
        user = CoroutineMock()
        backend = CoroutineMock(spec=UsersBackend)
        await self.service.update_user(user, backend)
        backend.update_user.assert_awaited_with(user)
