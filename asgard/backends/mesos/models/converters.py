from asgard.backends.models.converters import ModelConverterInterface
from asgard.clients.mesos.models.spec import (
    MesosUsedResourcesSpec,
    MesosResourcesSpec,
)
from asgard.models.spec.resources import UsedResourcesSpec, ResourcesSpec


class MesosUsedResourcesSpecConverter(
    ModelConverterInterface[UsedResourcesSpec, MesosUsedResourcesSpec]
):
    @staticmethod
    def to_asgard_model(other: MesosUsedResourcesSpec) -> UsedResourcesSpec:
        return UsedResourcesSpec(
            disk=other.disk, mem=other.mem, cpus=other.cpus
        )

    @staticmethod
    def to_client_model(other: UsedResourcesSpec) -> MesosUsedResourcesSpec:
        raise NotImplementedError


class MesosResourcesSpecConverter(
    ModelConverterInterface[ResourcesSpec, MesosResourcesSpec]
):
    @staticmethod
    def to_asgard_model(other: MesosResourcesSpec) -> ResourcesSpec:
        return UsedResourcesSpec(
            disk=other.disk, mem=other.mem, cpus=other.cpus
        )

    @staticmethod
    def to_client_model(other: ResourcesSpec) -> MesosResourcesSpec:
        raise NotImplementedError
