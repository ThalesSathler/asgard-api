from typing import List, Optional

from pydantic import BaseModel

from asgard.models.account import Account
from asgard.models.user import User


class AccountsResource(BaseModel):
    accounts: List[Account] = []


class AccountResource(BaseModel):
    account: Optional[Account]


class AccountUsersResource(BaseModel):
    users: List[User] = []
