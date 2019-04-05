import abc
from typing import List, Dict, Union, Optional, Any

from asgard.models.app import App, AppFactory
from asgard.models.base import BaseModel, ModelFactory


class Agent(BaseModel, abc.ABC):
    id: str
    hostname: str
    active: bool
    version: str
    port: int
    used_resources: Dict[str, Union[str, int]]
    attributes: Dict[str, str]
    resources: Dict[str, Union[str, int]]
    total_apps: int = 0
    applications: List[AppFactory] = []
    stats: Optional[Dict[str, Any]] = {}

    def has_attribute(self, attr_name):
        return attr_name in self.attributes

    def _get_attribute_value(self, attr_name):
        return self.attributes[attr_name]

    def attr_has_value(self, attr_name, attr_value):
        return (
            self.has_attribute(attr_name)
            and self._get_attribute_value(attr_name) == attr_value
        )

    @abc.abstractmethod
    def filter_by_attrs(self, attrs_kv):
        raise NotImplementedError

    @abc.abstractmethod
    async def apps(self) -> List[App]:
        raise NotImplementedError

    @abc.abstractmethod
    async def calculate_stats(self):
        raise NotImplementedError


AgentFactory = ModelFactory(Agent)
