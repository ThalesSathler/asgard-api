class Decision:
    def __init__(self, appid: str, cpu: float = None, mem: int = None):
        self.id = appid
        self.cpu = cpu
        self.mem = mem
