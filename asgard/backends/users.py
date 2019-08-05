from typing import List, Optional

import psycopg2
from sqlalchemy.orm.exc import NoResultFound

from asgard.db import AsgardDBSession
from asgard.exceptions import DuplicateEntity
from asgard.models.account import Account, AccountDB
from asgard.models.user import User, UserDB
from asgard.models.user_has_account import UserHasAccount


class UsersBackend:
    async def get_alternate_accounts(
        self, user: User, current_account: Account
    ) -> List[Account]:
        _, UserTable = await user.to_alchemy_obj()
        _, AccountTable = await current_account.to_alchemy_obj()

        _join = UserTable.__table__.join(
            UserHasAccount,
            UserTable.id == UserHasAccount.c.user_id,
            isouter=True,
        ).join(
            AccountTable.__table__,
            AccountTable.id == UserHasAccount.c.account_id,
            isouter=True,
        )
        async with AsgardDBSession() as s:
            accounts = (
                await s.query(AccountTable)
                .join(_join)
                .filter(UserTable.tx_email == user.email)
                .filter(AccountTable.id != current_account.id)
                .all()
            )
            all_acc = [await Account.from_alchemy_obj(acc) for acc in accounts]
        return all_acc

    async def get_accounts_from_user(self, user: User) -> List[Account]:
        async with AsgardDBSession() as s:
            _join = UserDB.__table__.join(
                UserHasAccount, UserDB.id == UserHasAccount.c.user_id
            ).join(
                AccountDB.__table__,
                AccountDB.__table__.c.id == UserHasAccount.c.account_id,
            )
            accounts = (
                await s.query(AccountDB.__table__)
                .join(_join)
                .filter(UserHasAccount.c.user_id == user.id)
                .all()
            )
            return [await Account.from_alchemy_obj(a) for a in accounts]

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            async with AsgardDBSession() as s:
                user = await s.query(UserDB).filter(UserDB.id == user_id).one()
                return await User.from_alchemy_obj(user)
        except NoResultFound:
            return None

    async def get_users(self) -> List[User]:
        """
        Lista todos os usuários do sistema, independente de qual conta
        esses usuários estão vinculados
        """
        async with AsgardDBSession() as s:
            return [
                await User.from_alchemy_obj(u)
                for u in await s.query(UserDB).all()
            ]

    async def create_user(self, user: User) -> User:
        user_db, userTable = await user.to_alchemy_obj()
        try:
            async with AsgardDBSession() as s:
                returned_values = await s.execute(
                    userTable.__table__.insert()
                    .values(tx_name=user.name, tx_email=user.email)
                    .return_defaults(userTable.id)
                )
                created_id = list(returned_values)[0].id
                return User(id=created_id, name=user.name, email=user.email)
        except psycopg2.IntegrityError as e:
            raise DuplicateEntity(e.pgerror)

    async def delete_user(self, user: User) -> User:
        async with AsgardDBSession() as s:
            _, userTable = await user.to_alchemy_obj()

            delete_acc_relation = UserHasAccount.delete().where(
                UserHasAccount.c.user_id == user.id
            )
            delete_user = userTable.__table__.delete().where(
                userTable.id == user.id
            )
            await s.execute(delete_acc_relation)
            await s.execute(delete_user)
            return user

    async def update_user(self, user: User) -> User:
        async with AsgardDBSession() as s:
            user_db, userTable = await user.to_alchemy_obj()
            update = (
                userTable.__table__.update()
                .where(userTable.id == user.id)
                .values(tx_name=user.name, tx_email=user.email)
            )
            try:
                await s.execute(update)
            except psycopg2.IntegrityError as e:
                raise DuplicateEntity(e.pgerror)
            return user
