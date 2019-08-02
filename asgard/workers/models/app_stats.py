class AppStats:

    def __init__(self, appid: str, type: str, cpu_pct: str, ram_pct: str, cpu_thr_pct: str):
        self.id = appid
        self.type = type
        self.cpu_pct = cpu_pct
        self.ram_pct = ram_pct
        self.cpu_thr_pct = cpu_thr_pct

    def __eq__(self, other):
        return self.id == other.id
