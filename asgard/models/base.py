from collections.abc import Mapping
from typing import Dict, Type, TypeVar, Generic, Tuple

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.api import DeclarativeMeta

BaseModelAlchemy = declarative_base()


class BaseModel(PydanticBaseModel):
    type: str
    errors: Dict[str, str] = {}

    def add_error(self, field_name, error_msg):
        self.errors[field_name] = error_msg

    async def from_alchemy_object(self, alchemy_obj) -> "BaseModel":
        raise NotImplementedError

    async def to_alchemy_obj(
        self
    ) -> Tuple[DeclarativeMeta, Type[DeclarativeMeta]]:
        raise NotImplementedError


def ModelFactory(subclass_marker: Type[BaseModel]):
    """
    Função usada apenas para modelos que são abstratos, ou seja,
    modelos onde temos múltiplos backends possíveis.
    Agent é um exemplo: Podemos ter múltiplos backends para um Agent (Mesos, etc).
    Quando o retorno dessa função é usada em um modelo serializável, cada implementação do modelo
    deve definit o valor do atributo `type`.
    """

    class _ModelFactory(PydanticBaseModel):
        def __new__(cls, *args, **kwargs) -> BaseModel:
            type_ = kwargs.pop("type")
            for subclass in subclass_marker.__subclasses__():
                if subclass.__fields__["type"].default == type_:
                    return subclass(*args, **kwargs)
            raise ValueError(
                f"'{type_}' is an invalid {subclass_marker} type. "
            )

    return _ModelFactory
