from typing import List

from asgard.conf import settings
from asgard.workers.autoscaler.decision_component_interface import (
    DecisionComponentInterface,
)
from asgard.workers.models.decision import Decision
from asgard.workers.models.scalable_app import ScalableApp


class DecisionComponent(DecisionComponentInterface):
    def decide_scaling_actions(
        self, apps_stats: List[ScalableApp]
    ) -> List[Decision]:
        decisions = []
        for app in apps_stats:
            decision = Decision(app.id)
            deploy_decision = False

            cpu_usage = app.app_stats.cpu_usage / 100
            mem_usage = app.app_stats.mem_usage / 100

            if app.is_set_to_scale_cpu():

                if (
                    cpu_usage
                    > app.cpu_threshold + settings.AUTOSCALER_MARGIN_THRESHOLD
                    or cpu_usage
                    < app.cpu_threshold - settings.AUTOSCALER_MARGIN_THRESHOLD
                ):
                    new_cpu = (
                        cpu_usage * app.cpu_allocated
                    ) / app.cpu_threshold

                    decision.cpu = (
                        app.min_cpu_scale_limit
                        if new_cpu < app.min_cpu_scale_limit
                        else new_cpu
                    )
                    decision.cpu = (
                        app.max_cpu_scale_limit
                        if new_cpu > app.max_cpu_scale_limit
                        else new_cpu
                    )

                    deploy_decision = True
            if app.is_set_to_scale_mem():
                if (
                    mem_usage
                    > app.mem_threshold + settings.AUTOSCALER_MARGIN_THRESHOLD
                    or mem_usage
                    < app.mem_threshold - settings.AUTOSCALER_MARGIN_THRESHOLD
                ):
                    decision.mem = (
                        mem_usage * app.mem_allocated
                    ) / app.mem_threshold

                    decision.mem = (
                        app.min_mem_scale_limit
                        if new_cpu < app.min_mem_scale_limit
                        else new_cpu
                    )
                    decision.mem = (
                        app.max_mem_scale_limit
                        if new_cpu > app.max_mem_scale_limit
                        else new_cpu
                    )

                    deploy_decision = True

            if deploy_decision:
                decisions.append(decision)

        return decisions
