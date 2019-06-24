from abc import ABC, abstractmethod


class DecisionComponentInterface(ABC):
    @abstractmethod
    def decide_scaling_actions(self, apps_stats):
        pass


class DecisionComponent(DecisionComponentInterface):
    def decide_scaling_actions(self, apps_stats):
        return {"ok": True}
