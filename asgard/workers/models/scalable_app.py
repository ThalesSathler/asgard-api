class ScalableApp:
    def __init__(
        self,
        appid,
        autoscale_cpu=None,
        autoscale_mem=None,
    ):
        self.id = appid
        self.autoscale_cpu = autoscale_cpu
        self.autoscale_mem = autoscale_mem

    def set_to_scale_cpu(self) -> bool:
        return self.autoscale_cpu is not None

    def set_to_scale_mem(self) -> bool:
        return self.autoscale_mem is not None

    def set_to_scale(self):
        return self.set_to_scale_cpu() or self.set_to_scale_mem()

    def __str__(self):
        return f"{{appid={self.id}, autoscale_cpu={self.autoscale_cpu}, autoscale_mem={self.autoscale_mem}}}"

    def __repr__(self):
        return self.__str__()
