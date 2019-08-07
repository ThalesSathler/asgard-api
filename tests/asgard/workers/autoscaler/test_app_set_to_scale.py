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
