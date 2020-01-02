from unittest.mock import NonCallableMock

from asynctest import TestCase

import asgard.workers.autoscaler.decision_events as events
from asgard.workers.autoscaler.simple_decision_component import (
    DecisionComponent,
)
from asgard.workers.models.app_stats import AppStats
from asgard.workers.models.scalable_app import ScalableApp


class TestDecisionComponent(TestCase):
    async def test_scales_app_when_difference_greater_than_5_percent(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=1.0,
                mem_allocated=1.0,
                cpu_threshold=0.5,
                mem_threshold=0.7,
                app_stats=AppStats(cpu_usage=44.99, mem_usage=75.01),
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(1, len(decisions))
        self.assertEqual("test", decisions[0].id)

    async def test_does_not_scale_app_when_difference_less_than_5_percent(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=1.0,
                mem_allocated=1.0,
                cpu_threshold=0.5,
                mem_threshold=0.7,
                app_stats=AppStats(cpu_usage=45.01, mem_usage=74.99),
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(0, len(decisions))

    async def test_does_not_make_cpu_decision_when_cpu_is_ignored(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=1.0,
                mem_allocated=1.0,
                cpu_threshold=None,
                mem_threshold=0.7,
                app_stats=AppStats(cpu_usage=80, mem_usage=30),
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(1, len(decisions), "makes decision for the app only")
        self.assertEqual("test", decisions[0].id, "returns the correct app")
        self.assertEqual(None, decisions[0].cpu, "does not return cpu decision")
        self.assertNotEqual(None, decisions[0].mem, "returns memory decision")

    async def test_does_not_make_memory_decision_when_memory_is_ignored(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=1.0,
                mem_allocated=1.0,
                cpu_threshold=0.7,
                mem_threshold=None,
                app_stats=AppStats(cpu_usage=80, mem_usage=30),
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(1, len(decisions), "makes decision for the app only")
        self.assertEqual("test", decisions[0].id, "returns the correct app")
        self.assertNotEqual(None, decisions[0].cpu, "returns cpu decision")
        self.assertEqual(
            None, decisions[0].mem, "does not return memory decision"
        )

    async def test_does_not_make_any_decision_when_everything_is_ignored(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=1.0,
                mem_allocated=1.0,
                cpu_threshold=None,
                mem_threshold=None,
                app_stats=AppStats(cpu_usage=80, mem_usage=30),
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(0, len(decisions), "does not return any decisions")

    async def test_scales_cpu_and_mem_to_correct_value(self):
        apps = [
            ScalableApp(
                "test1",
                cpu_allocated=3.5,
                mem_allocated=1.0,
                cpu_threshold=0.1,
                mem_threshold=0.1,
                app_stats=AppStats(cpu_usage=100, mem_usage=100),
            ),
            ScalableApp(
                "test2",
                cpu_allocated=3.5,
                mem_allocated=1.0,
                cpu_threshold=0.5,
                mem_threshold=0.7,
                app_stats=AppStats(cpu_usage=100, mem_usage=100),
            ),
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(2, len(decisions), "makes decisions for both apps")
        self.assertEqual(
            "test1", decisions[0].id, "returns correct apps in correct order"
        )
        self.assertEqual(
            "test2", decisions[1].id, "returns correct apps in correct order"
        )
        self.assertEqual(35, decisions[0].cpu, "decides correct values for cpu")
        self.assertEqual(
            10, decisions[0].mem, "decides correct values for memory"
        )
        self.assertEqual(7, decisions[1].cpu, "decides correct values for cpu")
        self.assertEqual(
            1.4286,
            round(decisions[1].mem, 4),
            "decides correct values for memory",
        )

    async def test_scales_memory_to_correct_value(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                mem_threshold=0.2,
                app_stats=AppStats(cpu_usage=41.29, mem_usage=62.62),
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(1, len(decisions), "did not return any decisions")
        self.assertEqual(400.768, decisions[0].mem)

    async def test_does_not_scale_cpu_below_min_scale_limit(self):
        min_cpu_limit = float("inf")
        max_cpu_limit = float("inf")
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                cpu_threshold=0.6,
                app_stats=AppStats(cpu_usage=41.29, mem_usage=62.62),
                min_cpu_scale_limit=min_cpu_limit,
                max_cpu_scale_limit=max_cpu_limit,
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(1, len(decisions), "did not return any decisions")
        self.assertGreaterEqual(
            min_cpu_limit,
            decisions[0].cpu,
            "cpu value is less than the min limit",
        )

    async def test_does_not_scale_mem_below_min_scale_limit(self):
        min_mem_limit = float("inf")
        max_mem_limit = float("inf")
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                mem_threshold=0.5,
                app_stats=AppStats(cpu_usage=41.29, mem_usage=35.0),
                min_mem_scale_limit=min_mem_limit,
                max_mem_scale_limit=max_mem_limit,
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(1, len(decisions), "did not return any decisions")
        self.assertGreaterEqual(
            min_mem_limit,
            decisions[0].mem,
            "mem value is less than the min limit",
        )

    async def test_does_not_scale_mem_above_max_scale_limit(self):
        max_mem_limit = float("-inf")
        min_mem_limit = float("-inf")
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                mem_threshold=0.5,
                app_stats=AppStats(cpu_usage=41.29, mem_usage=80.0),
                max_mem_scale_limit=max_mem_limit,
                min_mem_scale_limit=min_mem_limit,
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(1, len(decisions), "did not return any decisions")
        self.assertLessEqual(
            max_mem_limit,
            decisions[0].mem,
            "mem value is greater than the max limit",
        )

    async def test_does_not_scale_cpu_above_max_scale_limit(self):
        max_cpu_limit = float("-inf")
        min_cpu_limit = float("-inf")
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                cpu_threshold=0.2,
                app_stats=AppStats(cpu_usage=41.29, mem_usage=80.0),
                max_cpu_scale_limit=max_cpu_limit,
                min_cpu_scale_limit=min_cpu_limit,
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(1, len(decisions), "did not return any decisions")
        self.assertLessEqual(
            max_cpu_limit,
            decisions[0].cpu,
            "cpu value is greater than the max limit",
        )

    async def test_does_not_make_decision_when_there_are_no_stats(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                cpu_threshold=0.2,
                app_stats=None,
            )
        ]

        decider = DecisionComponent()
        decisions = decider.decide_scaling_actions(apps)

        self.assertEqual(0, len(decisions), "decision was made")

    async def test_logs_cpu_upscaling_decisions(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                cpu_threshold=0.2,
                app_stats=AppStats(cpu_usage=100, mem_usage=100),
            )
        ]
        mock_logger = NonCallableMock()

        decider = DecisionComponent(logger=mock_logger)
        decisions = decider.decide_scaling_actions(apps)

        mock_logger.info.assert_called()

        logged_dict = mock_logger.info.call_args[0][0]

        self.assertIn("appname", logged_dict, "did not log correct app id")
        self.assertEqual(
            apps[0].id, logged_dict["appname"], "did not log correct app id"
        )

        self.assertIn("event", logged_dict, "did not log an event")
        self.assertEqual(
            events.CPU_SCALE_UP,
            logged_dict["event"],
            "did not log correct event",
        )

        self.assertIn(
            "previous_value", logged_dict, "did not log previous CPU value"
        )
        self.assertEqual(
            logged_dict["previous_value"],
            apps[0].cpu_allocated,
            "did not log correct previous CPU value",
        )

        self.assertIn("new_value", logged_dict, "did not log new CPU value")
        self.assertEqual(
            logged_dict["new_value"],
            decisions[0].cpu,
            "did not log correct new CPU value",
        )

    async def test_logs_memory_upscaling_decisions(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                mem_threshold=0.2,
                app_stats=AppStats(cpu_usage=100, mem_usage=100),
            )
        ]
        mock_logger = NonCallableMock()

        decider = DecisionComponent(logger=mock_logger)
        decisions = decider.decide_scaling_actions(apps)

        mock_logger.info.assert_called()

        logged_dict = mock_logger.info.call_args[0][0]

        self.assertIn("appname", logged_dict, "did not log correct app id")
        self.assertEqual(
            apps[0].id, logged_dict["appname"], "did not log correct app id"
        )

        self.assertIn("event", logged_dict, "did not log an event")
        self.assertEqual(
            events.MEM_SCALE_UP,
            logged_dict["event"],
            "did not log correct event",
        )

        self.assertIn(
            "previous_value", logged_dict, "did not log previous memory value"
        )
        self.assertEqual(
            apps[0].mem_allocated,
            logged_dict["previous_value"],
            "did not log correct previous memory value",
        )

        self.assertIn("new_value", logged_dict, "did not log new memory value")
        self.assertEqual(
            decisions[0].mem,
            logged_dict["new_value"],
            "did not log correct new memory value",
        )

    def test_logs_cpu_downscaling_decisions(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                cpu_threshold=1,
                app_stats=AppStats(cpu_usage=1, mem_usage=1),
            )
        ]
        mock_logger = NonCallableMock()

        decider = DecisionComponent(logger=mock_logger)
        decisions = decider.decide_scaling_actions(apps)

        mock_logger.info.assert_called()

        logged_dict = mock_logger.info.call_args[0][0]

        self.assertIn("appname", logged_dict, "did not log correct app id")
        self.assertEqual(
            apps[0].id, logged_dict["appname"], "did not log correct app id"
        )

        self.assertIn("event", logged_dict, "did not log an event")
        self.assertEqual(
            events.CPU_SCALE_DOWN,
            logged_dict["event"],
            "did not log correct event",
        )

        self.assertIn(
            "previous_value", logged_dict, "did not log previous CPU value"
        )
        self.assertEqual(
            apps[0].cpu_allocated,
            logged_dict["previous_value"],
            "did not log correct previous CPU value",
        )

        self.assertIn("new_value", logged_dict, "did not log new CPU value")
        self.assertEqual(
            decisions[0].cpu,
            logged_dict["new_value"],
            "did not log correct new CPU value",
        )

    def test_logs_memory_downscaling_decisions(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                mem_threshold=1,
                app_stats=AppStats(cpu_usage=1, mem_usage=1),
            )
        ]
        mock_logger = NonCallableMock()

        decider = DecisionComponent(logger=mock_logger)
        decisions = decider.decide_scaling_actions(apps)

        mock_logger.info.assert_called()

        logged_dict = mock_logger.info.call_args[0][0]

        self.assertIn("appname", logged_dict, "did not log correct app id")
        self.assertEqual(
            apps[0].id, logged_dict["appname"], "did not log correct app id"
        )

        self.assertIn("event", logged_dict, "did not log an event")
        self.assertEqual(
            events.MEM_SCALE_DOWN,
            logged_dict["event"],
            "did not log correct event",
        )

        self.assertIn(
            "previous_value", logged_dict, "did not log previous memory value"
        )
        self.assertEqual(
            apps[0].mem_allocated,
            logged_dict["previous_value"],
            "did not log correct previous memory value",
        )

        self.assertIn("new_value", logged_dict, "did not log new memory value")
        self.assertEqual(
            decisions[0].mem,
            logged_dict["new_value"],
            "did not log correct new memory value",
        )

    def test_logs_cpu_and_memory_scaling_decisions(self):
        apps = [
            ScalableApp(
                "test",
                cpu_allocated=0.5,
                mem_allocated=128,
                mem_threshold=1,
                cpu_threshold=0.2,
                app_stats=AppStats(cpu_usage=100, mem_usage=1),
            )
        ]
        mock_logger = NonCallableMock()

        decider = DecisionComponent(logger=mock_logger)
        decisions = decider.decide_scaling_actions(apps)

        mock_logger.info.assert_called()

        logger_calls = [call[0][0] for call in mock_logger.info.call_args_list]

        self.assertEqual(len(logger_calls), 2, "did not call log.info 2 times")

        logger_calls.sort(key=lambda call: call["event"])

        cpu_log_dict = logger_calls[0]
        mem_log_dict = logger_calls[1]

        self.assertIn("appname", cpu_log_dict, "did not log correct app id")
        self.assertEqual(
            mem_log_dict["appname"], apps[0].id, "did not log correct app id"
        )

        self.assertIn("event", cpu_log_dict, "did not log an event")
        self.assertEqual(
            events.CPU_SCALE_UP,
            cpu_log_dict["event"],
            "did not log correct event",
        )

        self.assertIn(
            "previous_value", cpu_log_dict, "did not log previous memory value"
        )
        self.assertEqual(
            0.5,
            cpu_log_dict["previous_value"],
            "did not log correct previous memory value",
        )

        self.assertIn("new_value", cpu_log_dict, "did not log new memory value")
        self.assertEqual(
            decisions[0].cpu,
            cpu_log_dict["new_value"],
            "did not log correct new memory value",
        )

        self.assertIn("appname", mem_log_dict, "did not log correct app id")
        self.assertEqual(
            apps[0].id, mem_log_dict["appname"], "did not log correct app id"
        )

        self.assertIn("event", mem_log_dict, "did not log an event")
        self.assertEqual(
            events.MEM_SCALE_DOWN,
            mem_log_dict["event"],
            "did not log correct event",
        )

        self.assertIn(
            "previous_value", mem_log_dict, "did not log previous memory value"
        )
        self.assertEqual(
            apps[0].mem_allocated,
            mem_log_dict["previous_value"],
            "did not log correct previous memory value",
        )

        self.assertIn("new_value", mem_log_dict, "did not log new memory value")
        self.assertEqual(
            decisions[0].mem,
            mem_log_dict["new_value"],
            "did not log correct new memory value",
        )
