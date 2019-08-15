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
    ):
        self.id = appid
        self.cpu_allocated = cpu_allocated
        self.mem_allocated = mem_allocated
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold
        self.app_stats = app_stats

    def is_set_to_scale_cpu(self) -> bool:
        return self.cpu_threshold is not None

    def is_set_to_scale_mem(self) -> bool:
        return self.mem_threshold is not None

    def is_set_to_scale(self) -> bool:
        return self.is_set_to_scale_cpu() or self.is_set_to_scale_mem()

