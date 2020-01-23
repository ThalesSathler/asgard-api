from typing import List

from asgard.conf import settings
from asgard.workers.autoscaler.decision_component_interface import (
    DecisionComponentInterface,
)
from asgard.workers.autoscaler.decision_events import DecisionEvents
from asgard.workers.models.decision import Decision
from asgard.workers.models.scalable_app import ScalableApp
from hollowman.log import logger as default_logger


def _limit_number(number: float, min_value: float, max_value: float) -> float:
    return max(min(number, max_value), min_value)


class DecisionComponent(DecisionComponentInterface):
    def __init__(self, logger=default_logger):
        self.logger = logger

    def decide_scaling_actions(self, apps: List[ScalableApp]) -> List[Decision]:
        decisions = []
        for app in apps:
            if app.app_stats:
                decision = Decision(app.id)

                if app.cpu_needs_scaling():
                    new_cpu = (
                        app.get_cpu_usage() * app.cpu_allocated
                    ) / app.cpu_threshold

                    new_cpu = _limit_number(
                        new_cpu,
                        app.min_cpu_scale_limit,
                        app.max_cpu_scale_limit,
                    )

                    if new_cpu != app.cpu_allocated:
                        decision.cpu = new_cpu
                        event = (
                            DecisionEvents.CPU_SCALE_DOWN
                            if app.cpu_allocated > decision.cpu
                            else DecisionEvents.CPU_SCALE_UP
                        )
                        self.logger.info(
                            {
                                "appname": app.id,
                                "event": event,
                                "previous_value": app.cpu_allocated,
                                "new_value": decision.cpu,
                            }
                        )

                if app.is_set_to_scale_cpu() and decision.cpu is None:
                    self.logger.debug(
                        {
                            "appname": app.id,
                            "event": DecisionEvents.CPU_SCALE_NONE,
                            "reason": "usage within accepted margin",
                            "usage": app.get_cpu_usage(),
                            "threshold": app.cpu_threshold,
                            "accepted_margin": settings.AUTOSCALER_MARGIN_THRESHOLD,
                        }
                    )

                if app.mem_needs_scaling():
                    new_mem = (
                        app.get_mem_usage() * app.mem_allocated
                    ) / app.mem_threshold

                    new_mem = _limit_number(
                        new_mem,
                        app.min_mem_scale_limit,
                        app.max_mem_scale_limit,
                    )

                    if new_mem != app.mem_allocated:
                        decision.mem = new_mem

                        event = (
                            DecisionEvents.MEM_SCALE_DOWN
                            if app.mem_allocated > decision.mem
                            else DecisionEvents.MEM_SCALE_UP
                        )
                        self.logger.info(
                            {
                                "appname": app.id,
                                "event": event,
                                "previous_value": app.mem_allocated,
                                "new_value": decision.mem,
                            }
                        )

                if app.is_set_to_scale_mem() and decision.mem is None:
                    self.logger.debug(
                        {
                            "appname": app.id,
                            "event": DecisionEvents.MEM_SCALE_NONE,
                            "reason": "usage within accepted margin",
                            "usage": app.get_mem_usage(),
                            "threshold": app.mem_threshold,
                            "accepted_margin": settings.AUTOSCALER_MARGIN_THRESHOLD,
                        }
                    )

                if decision.mem is not None or decision.cpu is not None:
                    decisions.append(decision)

        return decisions
