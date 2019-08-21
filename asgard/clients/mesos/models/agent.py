from typing import Dict

from pydantic import BaseModel as PydanticBaseModel


class MesosAgent(PydanticBaseModel):
    id: str
    hostname: str
    port: int
    attributes: Dict[str, str]
    version: str
    active: bool
    used_resources: Dict[str, str]
    resources: Dict[str, str]

    def to_asgard_model(self, class_):
        return class_(**self.dict())
