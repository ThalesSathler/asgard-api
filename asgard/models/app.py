import abc

from .base import BaseModel, ModelFactory


class App(BaseModel, abc.ABC):
    id: str

    @abc.abstractclassmethod
    def transform_to_asgard_app_id(cls, name: str) -> str:
        raise NotImplementedError


class AppStats(BaseModel):
    type: str = "ASGARD"
    cpu_pct: str
    ram_pct: str
    cpu_thr_pct: str


AppFactory = ModelFactory(App)
