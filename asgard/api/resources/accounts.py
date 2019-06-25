from typing import List

from pydantic import BaseModel

from asgard.models.account import Account


class AccountsResource(BaseModel):
    accounts: List[Account] = []
