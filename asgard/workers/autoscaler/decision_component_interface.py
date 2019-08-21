from abc import ABC, abstractmethod
from typing import List

from asgard.workers.models.decision import Decision
from asgard.workers.models.scalable_app import ScalableApp


class DecisionComponentInterface(ABC):
    @abstractmethod
    def decide_scaling_actions(
        self, apps_stats: List[ScalableApp]
    ) -> List[Decision]:
        raise NotImplementedError
