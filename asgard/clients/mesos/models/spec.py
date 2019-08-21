from pydantic import BaseModel


class MesosUsedResourcesSpec(BaseModel):
    disk: float
    mem: float
    gpus: int
    cpus: float
    ports: str
