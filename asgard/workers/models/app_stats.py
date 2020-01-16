from typing import Optional


class AppStats:
    def __init__(self, cpu_usage: Optional[float] = None, mem_usage: Optional[float] = None):
        self.cpu_usage = cpu_usage
        self.mem_usage = mem_usage
