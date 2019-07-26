import abc
import re
from typing import List, Optional

from pydantic import validator

from asgard.models.account import Account
from asgard.models.base import BaseModel
from asgard.models.spec.constraint import ConstraintSpec, ConstraintSpecItem
from asgard.models.spec.container import ContainerSpec
from asgard.models.spec.env import EnvSpec
from asgard.models.spec.fetch import FetchURLSpec
from asgard.models.spec.schedule import ScheduleSpec


class AbstractApp(BaseModel, abc.ABC):
    @abc.abstractmethod
    def add_namespace(self, account: Account) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def remove_namespace(self, account: Account) -> "AbstractApp":
        raise NotImplementedError()


class App(AbstractApp):
    id: str
    command: Optional[str]
    arguments: Optional[List[str]]
    cpus: float
    mem: int
    disk: int = 0
    container: ContainerSpec
    env: Optional[EnvSpec]
    constraints: Optional[ConstraintSpec]
    fetch: Optional[List[FetchURLSpec]]

    def add_constraint(self, constraint: ConstraintSpecItem) -> "App":
        if not self.constraints:
            self.constraints = []
        self._remove_constraint_by_name(constraint.split(":")[0])
        self.constraints.append(constraint)
        return self

    def _remove_constraint_by_name(self, constraint_name: str) -> "App":
        self.constraints = [
            item
            for item in self.constraints or []
            if item.split(":")[0] != constraint_name
        ]
        return self


class ScheduledJob(App):
    """
    Modelo que representa uma tarefa agendada, que pode
    rodar em um intervalo de tempo qualquer.
    """

    description: str
    shell: bool = False
    retries: int = 2
    enabled: bool = True
    concurrent: bool = False
    schedule: ScheduleSpec

    @validator("id")
    def validate_id(cls, v):
        if v:
            if not re.match(r"^[a-z0-9-]+$", v):
                raise ValueError("id must match [a-z0-9-]+")
        return v

    def add_namespace(self, account: Account) -> None:
        """
        Adiciona ao id dessa App o namespace da Account `account`.
        Para ScheduledJob a formação do nome é diferente, pois o
        separador é "-".
        """
        self.id = f"{account.namespace}-{self.id}"

    def remove_namespace(self, account: Account) -> "ScheduledJob":
        if self.id.startswith(f"{account.namespace}-"):
            self.id = self.id.replace(f"{account.namespace}-", "", 1)

        return self
