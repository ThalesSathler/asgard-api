from abc import ABC, abstractmethod

from asgard.workers.models.app_stats import AppStats


class DecisionComponentInterface(ABC):
    @abstractmethod
    def decide_scaling_actions(self, apps_stats):
        pass


class DecisionComponent(DecisionComponentInterface):
    def decide_scaling_actions(self, apps_stats: AppStats):
        raise NotImplementedError
