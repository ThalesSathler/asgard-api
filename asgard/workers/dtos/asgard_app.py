from typing import Dict, Optional

from .converter_interface import Converter
from asgard.workers.models.scalable_app import ScalableApp
from asgard.workers.models.app_stats import AppStats
from pydantic import BaseModel


class AppDto(BaseModel):
    id: str
    cpu: float
    mem: float
    labels: Optional[Dict[str, str]]


class StatsSpec(BaseModel):
    type: str
    cpu_pct: str
    ram_pct: str
    cpu_thr_pct: str


class AppStatsDto(BaseModel):
    id: str
    stats: StatsSpec


class AppConverter(
    Converter[ScalableApp, AppDto]
):
    @classmethod
    def to_model(cls, dto_object: AppDto) -> ScalableApp:
        scalable_app = ScalableApp(dto_object.id)

        if dto_object.labels is not None:
            if "asgard.autoscale.ignore" in dto_object.labels:
                scalable_app.autoscale_ignore = dto_object.labels["asgard.autoscale.ignore"]

            if "asgard.autoscale.cpu" in dto_object.labels:
                scalable_app.autoscale_cpu = float(dto_object.labels["asgard.autoscale.cpu"])

            if "asgard.autoscale.mem" in dto_object.labels:
                scalable_app.autoscale_mem = float(dto_object.labels["asgard.autoscale.mem"])

        return scalable_app

    @classmethod
    def to_dto(cls, model_object: ScalableApp) -> AppDto:
        # conversao nao necessaria
        raise NotImplementedError


class AppStatsConverter (
    Converter[AppStats, AppStatsDto]
):
    @classmethod
    def to_model(cls, dto_object: AppStatsDto) -> AppStats:
        app_stats = AppStats(dto_object.id)
        app_stats.cpu_usage = float(dto_object.stats.cpu_pct)
        app_stats.ram_usage = float(dto_object.stats.ram_pct)

        return app_stats

    @classmethod
    def to_dto(cls, model_object: AppStats) -> AppStatsDto:
        # conversao nao necessaria
        raise NotImplementedError
