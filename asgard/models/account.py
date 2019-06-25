# encoding: utf-8

from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import relationship

from asgard.db import AsgardDBSession
from asgard.models.base import BaseModel, ModelFactory, BaseModelAlchemy
from asgard.models.user import User, UserDB
from asgard.models.user_has_account import UserHasAccount


class AccountDB(BaseModelAlchemy):  # type: ignore
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    users = relationship("UserDB", secondary=UserHasAccount)
    namespace = Column(String, nullable=False)
    owner = Column(String, nullable=False)


class Account(BaseModel):
    type: str = "ASGARD"
    id: int
    name: str
    namespace: str
    owner: str

    @staticmethod
    async def from_alchemy_obj(alchemy_obj: AccountDB) -> "Account":
        return Account(
            id=alchemy_obj.id,
            name=alchemy_obj.name,
            namespace=alchemy_obj.namespace,
            owner=alchemy_obj.owner,
        )

    async def to_alchemy_obj(self):
        return (
            AccountDB(
                id=self.id,
                name=self.name,
                namespace=self.namespace,
                owner=self.owner,
            ),
            AccountDB,
        )

    async def user_has_permission(self, user: User) -> bool:
        _join = UserHasAccount.join(
            UserDB, UserHasAccount.c.user_id == UserDB.id
        )
        async with AsgardDBSession() as s:
            has_permission = (
                await s.query(UserHasAccount.c.id)
                .join(_join)
                .filter(UserDB.tx_email == user.email)
                .filter(UserHasAccount.c.account_id == self.id)
                .exists()
            )
        return has_permission
