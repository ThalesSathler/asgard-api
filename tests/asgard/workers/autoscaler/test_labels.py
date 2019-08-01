from asynctest import TestCase

from asgard.workers.autoscaler.cloudinterface import AsgardInterface
from asgard.workers.models.scalable_app import ScalableApp


class LabelsTest(TestCase):
    def test_application_should_be_scaled(self):
        fixture = {
            "id": "test_app1",
            "cpu": 0,
            "mem": 0,
            "labels": {
                "asgard.autoscale.cpu": 0.3,
                "asgard.autoscale.mem": 0.8,
            }
        }
        scaler = AsgardInterface()

        should_scale = scaler.should_scale(ScalableApp(**fixture))

        self.assertEqual(True, should_scale)

    def test_application_should_be_scaled_cpu(self):
        fixture = {
            "id": "test_app1",
            "cpu": 0,
            "mem": 0,
            "labels": {
                "asgard.autoscale.cpu": 0.3,
            }
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(ScalableApp(**fixture))

        self.assertEqual(True, should_scale)

    def test_application_should_be_scaled_mem(self):
        fixture = {
            "id": "test_app1",
            "cpu": 0,
            "mem": 0,
            "labels": {
                "asgard.autoscale.mem": 0.8,
            }
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(ScalableApp(**fixture))

        self.assertEqual(True, should_scale)

    def test_application_should_not_be_scaled_missing_needed_labels(self):
        fixture = {
            "id": "test_app1",
            "cpu": 0,
            "mem": 0,
            "labels": {}
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(ScalableApp(**fixture))

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_label_ignore_all(self):
        fixture = {
            "id": "test_app1",
            "cpu": 0,
            "mem": 0,
            "labels": {
                "asgard.autoscale.cpu": 0.3,
                "asgard.autoscale.mem": 0.8,
                "asgard.autoscale.ignore": "all",
            },
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(ScalableApp(**fixture))

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_all_individual_labels_ignored(
        self
    ):
        fixture = {
            "id": "test_app1",
            "cpu": 0,
            "mem": 0,
            "labels": {
                "asgard.autoscale.cpu": 0.3,
                "asgard.autoscale.mem": 0.8,
                "asgard.autoscale.ignore": "cpu,mem",
            },
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(ScalableApp(**fixture))

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_only_has_cpu_and_cpu_ignored(
        self
    ):
        fixture = {
            "id": "test_app1",
            "cpu": 0,
            "mem": 0,
            "labels": {
                "asgard.autoscale.cpu": 0.3,
                "asgard.autoscale.ignore": "cpu",
            },
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(ScalableApp(**fixture))

        self.assertEqual(False, should_scale)

    def test_application_should_not_be_scaled_only_has_mem_and_mem_ignored(
        self
    ):
        fixture = {
            "id": "test_app1",
            "cpu": 0,
            "mem": 0,
            "labels": {
                "asgard.autoscale.mem": 0.3,
                "asgard.autoscale.ignore": "mem",
            },
        }

        scaler = AsgardInterface()

        should_scale = scaler.should_scale(ScalableApp(**fixture))

        self.assertEqual(False, should_scale)
