class AppStats:

    def __init__(
            self,
            app_id: str,
            cpu_usage: float = None,
            ram_usage: float = None,
            allocated_cpu: float = None,
            allocated_ram: float = None
    ):
        self.id = app_id
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage
        self.allocated_cpu = allocated_cpu
        self.allocated_ram = allocated_ram
