from abc import ABC, abstractmethod
from typing import Dict, List

import asgard.clients.apps.client as asgard_client
from asgard.workers.converters.asgard_converter import (
    AppConverter,
    AppStatsConverter,
    DecisionConverter,
)
from asgard.workers.models.app_stats import AppStats
from asgard.workers.models.decision import Decision
from asgard.workers.models.scalable_app import ScalableApp


class CloudInterface(ABC):
    @abstractmethod
    async def fetch_all_apps(self) -> List[ScalableApp]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_scalable_apps(self) -> List[ScalableApp]:
        raise NotImplementedError

    @abstractmethod
    async def get_app_stats(self, app_id) -> AppStats:
        raise NotImplementedError

    @abstractmethod
    async def apply_decisions(
        self, scaling_decisions: Decision
    ) -> List[Decision]:
        raise NotImplementedError
