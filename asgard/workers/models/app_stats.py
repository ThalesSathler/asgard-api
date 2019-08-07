class AppStats:

    def __init__(
            self,
            cpu_usage: float = None,
            ram_usage: float = None,
            allocated_cpu: float = None,
            allocated_ram: float = None
    ):
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage
        self.allocated_cpu = allocated_cpu
        self.allocated_ram = allocated_ram
