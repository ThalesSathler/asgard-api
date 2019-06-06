from asynctest import TestCase
from asgard.workers.autoscaler.cloudinterface import AsgardCloudInterface
from asgard.workers.autoscaler.decisioncomponent import DecisionComponent
from asgard.workers.autoscaler.periodicstatechecker import PeriodicStateChecker


class AutoscalerTest(TestCase):
    def test_scale_one_app(self):
        cloud_interface = AsgardCloudInterface()
        state_checker = PeriodicStateChecker(cloud_interface)
        decision_maker = DecisionComponent()

        apps_stats = state_checker.get_scalable_apps_stats()
        scaling_decision = decision_maker.decide_scaling_actions(apps_stats)
        cloud_interface.scale_apps(scaling_decision)

        self.assertTrue(False)

    def test_decide_to_scale_all_apps(self):
        self.assertTrue(False)

    def test_decide_to_scale_some_apps(self):
        self.assertTrue(False)

    def test_decide_to_scale_no_app(self):
        self.assertTrue(False)