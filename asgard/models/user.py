# encoding: utf-8

from typing import Type, Tuple, Optional

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from asgard.models.base import BaseModel, ModelFactory, BaseModelAlchemy
from asgard.models.user_has_account import UserHasAccount


class UserDB(BaseModelAlchemy):  # type: ignore
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    accounts = relationship("AccountDB", secondary=UserHasAccount)
    tx_name = Column(String, nullable=False)
    tx_email = Column(String, nullable=False, unique=True)
    tx_authkey = Column(String(32), nullable=True, unique=True)
    bl_system = Column(Boolean, nullable=False, default=False)


class User(BaseModel):
    type: str = "ASGARD"
    id: Optional[int]
    name: Optional[str]
    email: Optional[str]

    @staticmethod
    async def from_alchemy_obj(alchemy_obj: UserDB) -> "User":
        return User(
            id=alchemy_obj.id,
            name=alchemy_obj.tx_name,
            email=alchemy_obj.tx_email,
        )

    async def to_alchemy_obj(self) -> Tuple[UserDB, Type[UserDB]]:
        return (
            UserDB(id=self.id, tx_name=self.name, tx_email=self.email),
            UserDB,
        )


UserFactory = ModelFactory(User)
