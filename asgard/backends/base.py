import abc
from enum import Enum
from typing import List, Optional

from asgard.models.account import Account
from asgard.models.agent import Agent
from asgard.models.app import App, AppStats
from asgard.models.user import User


class Interval(str, Enum):
    ONE_HOUR = "1h"
    ONE_MINUTE = "1m"


class AppsBackend(abc.ABC):
    @abc.abstractmethod
    async def get_app_stats(
        self, app: App, interval: Interval, user: User, account: Account
    ) -> AppStats:
        raise NotImplementedError


class AgentsBackend(abc.ABC):
    @abc.abstractmethod
    async def get_agents(self, user: User, account: Account) -> List[Agent]:
        """
        Retorna todos os Agents da conta `account`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, agentd_id: str, user: User, account: Account
    ) -> Optional[Agent]:
        """
        Retorna o agent de id `agentd_id` pertencente à conta `account`
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_apps_running(self, user: User, agent: Agent) -> List[App]:
        """
        Retornas lista de App que está rodando nesse agent
        """
        raise NotImplementedError


class Orchestrator(metaclass=abc.ABCMeta):
    """
    Classe abstrata que mapeia todas as ações que um orquestrador pode excutar.
    As depdenências injetadas aqui são implementações que efetivamente falam com cada um dos backends suportados.
    """

    def __init__(
        self, agents_backend: AgentsBackend, apps_backend: AppsBackend
    ) -> None:
        self.agents_backend = agents_backend
        self.apps_backend = apps_backend

    @abc.abstractmethod
    async def get_agents(self, user: User, account: Account) -> List[Agent]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_apps_running_for_agent(
        self, user: User, agent: Agent
    ) -> List[App]:
        """
        Método que retorna todas as apps que estão atualmente rodando no agent referido.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_agent_by_id(
        self, agent_id: str, user: User, account: Account
    ) -> Optional[Agent]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_app_stats(
        self, app: App, interval: Interval, user: User, account: Account
    ) -> AppStats:
        raise NotImplementedError
