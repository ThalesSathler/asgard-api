from abc import ABC, abstractmethod
from typing import List

from asgard.workers.models.app_stats import AppStats
from asgard.workers.models.scaling_decision import Decision


class DecisionComponentInterface(ABC):
    @abstractmethod
    def decide_scaling_actions(self, apps_stats: AppStats) -> Decision:
        pass


class DecisionComponent(DecisionComponentInterface):
    def decide_scaling_actions(self, apps_stats: AppStats) -> Decision:
        raise NotImplementedError
