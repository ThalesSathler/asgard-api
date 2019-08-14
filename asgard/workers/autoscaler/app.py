from asyncworker import App

from asgard.workers.autoscaler.asgard_cloudinterface import AsgardInterface
from asgard.workers.autoscaler.periodicstatechecker import PeriodicStateChecker
from asgard.workers.autoscaler.simple_decision_component import (
    DecisionComponent,
)

app = App("", "", "", 123)


@app.run_every(60)
async def scale_all_apps(app: App):
    cloud_interface = AsgardInterface()
    state_checker = PeriodicStateChecker(cloud_interface)
    decision_maker = DecisionComponent()

    apps_stats = await state_checker.get_scalable_apps_stats()
    scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
    await cloud_interface.apply_decisions(scaling_decision)
