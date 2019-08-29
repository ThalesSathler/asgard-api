from pydantic import BaseModel

from asgard.clients.mesos.models.spec import (
    MesosAttributesSpec,
    MesosResourcesSpec,
    MesosUsedResourcesSpec,
)


class MesosAgent(BaseModel):
    id: str
    hostname: str
    port: int
    attributes: MesosAttributesSpec
    version: str
    active: bool
    used_resources: MesosUsedResourcesSpec
    resources: MesosResourcesSpec
