from asynctest import TestCase
from asgard.workers.autoscaler.cloudinterface import AsgardInterface


class LabelsTest(TestCase):
    def test_application_should_be_scaled(self):
        fixture = {"asgard.autoscale.cpu": 0.3, "asgard.autoscale.mem": 0.8}

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(True, should_scale)

    def test_application_should_be_scaled_cpu(self):
        fixture = {"asgard.autoscale.cpu": 0.3}

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(True, should_scale)

    def test_application_should_be_scaled_mem(self):
        fixture = {"asgard.autoscale.mem": 0.8}

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(True, should_scale)

    def test_application_should_not_be_scaled_missing_needed_labels(self):
        fixture = {}

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_label_ignore_all(self):
        fixture = {
            "asgard.autoscale.cpu": 0.3,
            "asgard.autoscale.mem": 0.8,
            "asgard.autoscale.ignore": "all",
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_all_individual_labels_ignored(
        self
    ):
        fixture = {
            "asgard.autoscale.cpu": 0.3,
            "asgard.autoscale.mem": 0.8,
            "asgard.autoscale.ignore": "cpu;mem",
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_only_has_cpu_and_cpu_ignored(
        self
    ):
        fixture = {
            "asgard.autoscale.cpu": 0.3,
            "asgard.autoscale.ignore": "cpu",
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_only_has_mem_and_mem_ignored(
        self
    ):
        fixture = {
            "asgard.autoscale.mem": 0.3,
            "asgard.autoscale.ignore": "mem",
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(False, should_scale)
