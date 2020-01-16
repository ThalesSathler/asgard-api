from asgard.conf import settings
from asgard.workers.models.app_stats import AppStats


class ScalableApp:
    def __init__(
        self,
        appid: str,
        cpu_allocated: float = None,
        mem_allocated: float = None,
        cpu_threshold: float = None,
        mem_threshold: float = None,
        app_stats: AppStats = None,
        min_cpu_scale_limit: float = settings.MIN_CPU_SCALE_LIMIT,
        max_cpu_scale_limit: float = settings.MAX_CPU_SCALE_LIMIT,
        min_mem_scale_limit: float = settings.MIN_MEM_SCALE_LIMIT,
        max_mem_scale_limit: float = settings.MAX_MEM_SCALE_LIMIT,
    ):
        self.id = appid
        self.cpu_allocated = cpu_allocated
        self.mem_allocated = mem_allocated
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold
        self.app_stats = app_stats
        self.min_cpu_scale_limit = min_cpu_scale_limit
        self.max_cpu_scale_limit = max_cpu_scale_limit
        self.min_mem_scale_limit = min_mem_scale_limit
        self.max_mem_scale_limit = max_mem_scale_limit

    def is_set_to_scale_cpu(self) -> bool:
        return self.cpu_threshold is not None

    def is_set_to_scale_mem(self) -> bool:
        return self.mem_threshold is not None

    def is_set_to_scale(self) -> bool:
        return self.is_set_to_scale_cpu() or self.is_set_to_scale_mem()

    def get_cpu_usage(self) -> float:
        return self.app_stats.cpu_usage

    def get_mem_usage(self) -> float:
        return self.app_stats.mem_usage

    def cpu_needs_scaling(self) -> bool:
        return (
            abs(self.get_cpu_usage() - self.cpu_threshold)
            > settings.AUTOSCALER_MARGIN_THRESHOLD
        )

    def mem_needs_scaling(self) -> bool:
        return (
            abs(self.get_mem_usage() - self.mem_threshold)
            > settings.AUTOSCALER_MARGIN_THRESHOLD
        )
