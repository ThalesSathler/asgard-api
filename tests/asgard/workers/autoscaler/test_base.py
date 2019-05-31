from asynctest import TestCase
from asgard.workers.base import Autoscaler


class AutoscalerTest(TestCase):
    def test_application_should_be_scaled(self):
        fixture = {"asgard.autoscale.cpu": 0.3, "asgard.autoscale.mem": 0.8}

        scaler = Autoscaler()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(True, should_scale)

    def test_application_should_be_scaled_cpu(self):
        fixture = {"asgard.autoscale.cpu": 0.3}

        scaler = Autoscaler()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(True, should_scale)

    def test_application_should_be_scaled_mem(self):
        fixture = {"asgard.autoscale.mem": 0.8}

        scaler = Autoscaler()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(True, should_scale)

    def test_application_should_not_be_scaled_missing_needed_labels(self):
        fixture = {}

        scaler = Autoscaler()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_label_ignore_all(self):
        fixture = {
            "asgard.autoscale.cpu": 0.3,
            "asgard.autoscale.mem": 0.8,
            "asgard.autoscale.ignore": "all",
        }

        scaler = Autoscaler()

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

        scaler = Autoscaler()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_only_has_cpu_and_cpu_ignored(
        self
    ):
        fixture = {
            "asgard.autoscale.cpu": 0.3,
            "asgard.autoscale.ignore": "cpu",
        }

        scaler = Autoscaler()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_only_has_mem_and_mem_ignored(
        self
    ):
        fixture = {
            "asgard.autoscale.mem": 0.3,
            "asgard.autoscale.ignore": "mem",
        }

        scaler = Autoscaler()

        should_scale = scaler.should_scale(fixture)

        self.assertEqual(False, should_scale)
