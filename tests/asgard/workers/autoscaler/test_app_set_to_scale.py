from asynctest import TestCase

from asgard.workers.models.scalable_app import ScalableApp


class TestAppSetToScale(TestCase):
    def test_everything_should_be_scaled(self):
        app = ScalableApp("test_app1", cpu_threshold=0.3, mem_threshold=0.8)

        set_to_scale = app.is_set_to_scale()
        set_to_scale_cpu = app.is_set_to_scale_cpu()
        set_to_scale_mem = app.is_set_to_scale_mem()

        self.assertEqual(True, set_to_scale)
        self.assertEqual(True, set_to_scale_cpu)
        self.assertEqual(True, set_to_scale_mem)

    def test_only_cpu_should_be_scaled(self):
        app = ScalableApp("test_app1", cpu_threshold=0.3)

        set_to_scale = app.is_set_to_scale()
        set_to_scale_cpu = app.is_set_to_scale_cpu()
        set_to_scale_mem = app.is_set_to_scale_mem()

        self.assertEqual(True, set_to_scale)
        self.assertEqual(True, set_to_scale_cpu)
        self.assertEqual(False, set_to_scale_mem)

    def test_only_mem_should_be_scaled(self):
        app = ScalableApp("test_app1", mem_threshold=0.8)

        set_to_scale = app.is_set_to_scale()
        set_to_scale_cpu = app.is_set_to_scale_cpu()
        set_to_scale_mem = app.is_set_to_scale_mem()

        self.assertEqual(True, set_to_scale)
        self.assertEqual(False, set_to_scale_cpu)
        self.assertEqual(True, set_to_scale_mem)

    def test_application_should_not_be_scaled_missing_attributes(self):
        app = ScalableApp("id")

        set_to_scale = app.is_set_to_scale()
        set_to_scale_cpu = app.is_set_to_scale_cpu()
        set_to_scale_mem = app.is_set_to_scale_mem()

        self.assertEqual(False, set_to_scale)
        self.assertEqual(False, set_to_scale_cpu)
        self.assertEqual(False, set_to_scale_mem)

    # def test_application_should_not_be_scaled_label_ignore_all(self):
    #     fixture = ScalableApp(
    #         "test_app1",
    #         cpu_threshold=0.3,
    #         mem_threshold=0.8,
    #         autoscale_ignore="all",
    #     )
    #
    #     scaler = AsgardInterface()
    #
    #     set_to_scale = scaler.set_to_scale(fixture)
    #
    #     self.assertEqual(False, set_to_scale)
    #
    # def test_application_should_not_be_scaled_all_individual_labels_ignored(
    #     self
    # ):
    #     fixture = ScalableApp(
    #         "test_app1",
    #         cpu_threshold=0.3,
    #         mem_threshold=0.8,
    #         autoscale_ignore="cpu;mem",
    #     )
    #
    #     scaler = AsgardInterface()
    #
    #     set_to_scale = scaler.set_to_scale(fixture)
    #
    #     self.assertEqual(False, set_to_scale)
    #
    # def test_application_should_not_be_scaled_only_has_cpu_and_cpu_ignored(
    #     self
    # ):
    #     fixture = ScalableApp(
    #         "test_app1", cpu_threshold=0.3, autoscale_ignore="cpu"
    #     )
    #
    #     scaler = AsgardInterface()
    #
    #     set_to_scale = scaler.set_to_scale(fixture)
    #
    #     self.assertEqual(False, set_to_scale)
    #
    # def test_application_should_not_be_scaled_only_has_mem_and_mem_ignored(
    #     self
    # ):
    #     fixture = ScalableApp(
    #         "test_app1", mem_threshold=0.3, autoscale_ignore="mem"
    #     )
    # 
    #     scaler = AsgardInterface()
    #
    #     set_to_scale = scaler.set_to_scale(fixture)
    #
    #     self.assertEqual(False, set_to_scale)
