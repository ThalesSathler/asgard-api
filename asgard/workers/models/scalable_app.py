# from asgard.models.app import App

class ScalableApp:
    def __init__(
        self,
        appid,
        autoscale_ignore=None,
        autoscale_cpu=None,
        autoscale_mem=None,
    ):
        self.id = appid
        self.autoscale_ignore = autoscale_ignore
        self.autoscale_cpu = autoscale_cpu
        self.autoscale_mem = autoscale_mem


    def __eq__(self, other) -> bool:
        return other.id == self.id