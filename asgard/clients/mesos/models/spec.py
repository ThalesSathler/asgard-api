from typing import Dict, Optional

from pydantic import BaseModel


class MesosUsedResourcesSpec(BaseModel):
    disk: float
    mem: float
    gpus: int
    cpus: float
    ports: Optional[str]


class MesosResourcesSpec(BaseModel):
    disk: float
    mem: float
    gpus: int
    cpus: float
    ports: str


MesosAttributesSpec = Dict[str, str]
