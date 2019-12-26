from typing import List

from asgard.conf import settings
from asgard.workers.autoscaler.decision_component_interface import (
    DecisionComponentInterface,
)
from asgard.workers.models.decision import Decision
from asgard.workers.models.scalable_app import ScalableApp
from hollowman.log import logger as default_logger


class DecisionComponent(DecisionComponentInterface):
    def __init__(self, logger=default_logger):
        self.logger = logger

    def decide_scaling_actions(self, apps: List[ScalableApp]) -> List[Decision]:
        decisions = []
        for app in apps:
            if app.app_stats:
                decision = Decision(app.id)
                deploy_decision = False

                cpu_usage = app.app_stats.cpu_usage / 100
                mem_usage = app.app_stats.mem_usage / 100

                if app.is_set_to_scale_cpu():

                    if (
                        cpu_usage
                        > app.cpu_threshold
                        + settings.AUTOSCALER_MARGIN_THRESHOLD
                        or cpu_usage
                        < app.cpu_threshold
                        - settings.AUTOSCALER_MARGIN_THRESHOLD
                    ):
                        new_cpu = (
                            cpu_usage * app.cpu_allocated
                        ) / app.cpu_threshold

                        decision.cpu = (
                            app.min_cpu_scale_limit
                            if new_cpu < app.min_cpu_scale_limit
                            else app.max_cpu_scale_limit
                            if new_cpu > app.max_cpu_scale_limit
                            else new_cpu
                        )

                        self.logger.info(
                            {
                                "appid": app.id,
                                "event": "CPU_SCALE",
                                "previous_value": app.cpu_allocated,
                                "new_value": decision.cpu,
                            }
                        )

                        deploy_decision = True
                if app.is_set_to_scale_mem():
                    if (
                        mem_usage
                        > app.mem_threshold
                        + settings.AUTOSCALER_MARGIN_THRESHOLD
                        or mem_usage
                        < app.mem_threshold
                        - settings.AUTOSCALER_MARGIN_THRESHOLD
                    ):
                        new_mem = (
                            mem_usage * app.mem_allocated
                        ) / app.mem_threshold

                        decision.mem = (
                            app.min_mem_scale_limit
                            if new_mem < app.min_mem_scale_limit
                            else app.max_mem_scale_limit
                            if new_mem > app.max_mem_scale_limit
                            else new_mem
                        )

                        self.logger.info(
                            {
                                "appid": app.id,
                                "event": "MEM_SCALE",
                                "previous_value": app.mem_allocated,
                                "new_value": decision.mem,
                            }
                        )

                        deploy_decision = True

                if deploy_decision:
                    decisions.append(decision)

        return decisions
