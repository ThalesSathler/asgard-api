from typing import Optional, List

from sqlalchemy.orm.exc import NoResultFound

from asgard.db import AsgardDBSession
from asgard.models.account import Account, AccountDB


class AccountsBackend:
    async def get_account_by_id(self, acc_id: int) -> Optional[Account]:
        try:
            async with AsgardDBSession() as s:
                result = (
                    await s.query(AccountDB)
                    .filter(AccountDB.id == acc_id)
                    .one()
                )
                return await Account.from_alchemy_obj(result)
        except NoResultFound:
            return None

    async def get_accounts(self) -> List[Account]:
        async with AsgardDBSession() as s:
            result = await s.query(AccountDB).all()
            accounts = [await Account.from_alchemy_obj(item) for item in result]
            return accounts
