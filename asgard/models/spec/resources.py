from pydantic import BaseModel


class UsedResourcesSpec(BaseModel):
    disk: float
    mem: float
    cpus: float
