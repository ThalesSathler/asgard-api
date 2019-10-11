from asgard.backends.mesos.models.agent import MesosAgent
from asgard.backends.models.converters import ModelConverterInterface
from asgard.clients.mesos.models.agent import MesosAgent as MesosClientAgent
from asgard.clients.mesos.models.spec import (
    MesosUsedResourcesSpec,
    MesosResourcesSpec,
    MesosAttributesSpec,
)
from asgard.models.spec.attributes import AttributesSpec
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
        return ResourcesSpec(disk=other.disk, mem=other.mem, cpus=other.cpus)

    @staticmethod
    def to_client_model(other: ResourcesSpec) -> MesosResourcesSpec:
        raise NotImplementedError


class MesosAttrbutesSpecConverter(
    ModelConverterInterface[AttributesSpec, MesosAttributesSpec]
):
    @staticmethod
    def to_asgard_model(other: MesosAttributesSpec) -> AttributesSpec:
        return dict(**other)

    @staticmethod
    def to_client_model(other: AttributesSpec) -> MesosAttributesSpec:
        raise NotImplementedError


class MesosAgentConverter(
    ModelConverterInterface[MesosAgent, MesosClientAgent]
):
    @staticmethod
    def to_asgard_model(other: MesosClientAgent) -> MesosAgent:
        return MesosAgent(
            id=other.id,
            hostname=other.hostname,
            port=other.port,
            attributes=MesosAttrbutesSpecConverter.to_asgard_model(
                other.attributes
            ),
            version=other.version,
            active=other.active,
            used_resources=MesosUsedResourcesSpecConverter.to_asgard_model(
                other.used_resources
            ),
            resources=MesosResourcesSpecConverter.to_asgard_model(
                other.resources
            ),
        )

    @staticmethod
    def to_client_model(other: MesosAgent) -> MesosClientAgent:
        raise NotImplementedError
