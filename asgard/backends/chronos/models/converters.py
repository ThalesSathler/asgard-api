from typing import List

from asgard.backends.models.converters import ModelConverterInterface
from asgard.clients.chronos.models.job import (
    ChronosJob,
    ChronosContainerParameterSpec,
    ChronosContainerVolumeSpec,
    ChronosContainerSpec,
    ChronosEnvSpec,
    ChronosFetchURLSpec,
    ChronosConstraintSpec,
)
from asgard.models.job import ScheduledJob
from asgard.models.spec.constraint import ConstraintSpec
from asgard.models.spec.container import (
    ContainerSpec,
    ContainerParameterSpec,
    ContainerVolumeSpec,
)
from asgard.models.spec.env import EnvSpec
from asgard.models.spec.fetch import FetchURLSpec
from asgard.models.spec.schedule import ScheduleSpec


class ChronosScheduledJobConverter(
    ModelConverterInterface[ScheduledJob, ChronosJob]
):
    @classmethod
    def to_asgard_model(cls, other: ChronosJob) -> ScheduledJob:
        env_dict = None
        fetch_list = None
        constraints_list = None
        if other.environmentVariables:
            env_dict = ChronosEnvSpecConverter.to_asgard_model(
                other.environmentVariables
            )

        if other.fetch:
            fetch_list = ChronosFetchURLSpecConverter.to_asgard_model(
                other.fetch
            )

        if other.constraints:
            constraints_list = ChronosConstraintSpecConverter.to_asgard_model(
                other.constraints
            )
        return ScheduledJob(
            id=other.name,
            description=other.description,
            command=other.command,
            arguments=other.arguments,
            cpus=other.cpus,
            mem=other.mem,
            disk=other.disk,
            pull_image=other.container.forcePullImage,
            enabled=not other.disabled,
            shell=other.shell,
            container=ChronosContainerSpecConverter.to_asgard_model(
                other.container
            ),
            schedule=ScheduleSpec(
                value=other.schedule, tz=other.scheduleTimeZone
            ),
            env=env_dict,
            fetch=fetch_list,
            constraints=constraints_list,
        )

    @classmethod
    def to_client_model(cls, other: ScheduledJob) -> ChronosJob:
        env_list = None
        fetch_list = None
        constraints_list = None
        if other.env:
            env_list = ChronosEnvSpecConverter.to_client_model(other.env)

        if other.fetch:
            fetch_list = ChronosFetchURLSpecConverter.to_client_model(
                other.fetch
            )

        if other.constraints:
            constraints_list = ChronosConstraintSpecConverter.to_client_model(
                other.constraints
            )
        return ChronosJob(
            name=other.id,
            command=other.command,
            arguments=other.arguments,
            description=other.description,
            cpus=other.cpus,
            shell=other.shell,
            retires=other.retries,
            disabled=not other.enabled,
            concurrent=other.concurrent,
            mem=other.mem,
            disk=other.disk,
            schedule=other.schedule.value,
            scheduleTimeZone=other.schedule.tz,
            container=ChronosContainerSpecConverter.to_client_model(
                other.container
            ),
            environmentVariables=env_list,
            fetch=fetch_list,
            constraints=constraints_list,
        )


class ChronosContainerParameterSpecConverter(
    ModelConverterInterface[
        ContainerParameterSpec, ChronosContainerParameterSpec
    ]
):
    @classmethod
    def to_asgard_model(
        cls, other: ChronosContainerParameterSpec
    ) -> ContainerParameterSpec:
        return ContainerParameterSpec(name=other.key, value=other.value)

    @classmethod
    def to_client_model(
        cls, other: ContainerParameterSpec
    ) -> ChronosContainerParameterSpec:
        return ChronosContainerParameterSpec(key=other.name, value=other.value)


class ChronosContainerVolumeSpecConverter(
    ModelConverterInterface[ContainerVolumeSpec, ChronosContainerVolumeSpec]
):
    @classmethod
    def to_asgard_model(
        cls, other: ChronosContainerVolumeSpec
    ) -> ContainerVolumeSpec:
        return ContainerVolumeSpec(
            container_path=other.containerPath,
            host_path=other.hostPath,
            mode=other.mode,
        )

    @classmethod
    def to_client_model(
        cls, other: ContainerVolumeSpec
    ) -> ChronosContainerVolumeSpec:
        return ChronosContainerVolumeSpec(
            hostPath=other.host_path,
            containerPath=other.container_path,
            mode=other.mode,
        )


class ChronosContainerSpecConverter(
    ModelConverterInterface[ContainerSpec, ChronosContainerSpec]
):
    @classmethod
    def to_asgard_model(cls, other: ChronosContainerSpec) -> ContainerSpec:
        params = None
        volumes = None
        if other.parameters:
            params = [
                ChronosContainerParameterSpecConverter.to_asgard_model(p)
                for p in other.parameters
            ]
        if other.volumes:
            volumes = [
                ChronosContainerVolumeSpecConverter.to_asgard_model(v)
                for v in other.volumes
            ]
        return ContainerSpec(
            image=other.image,
            network=other.network,
            parameters=params,
            pull_image=other.forcePullImage,
            volumes=volumes,
        )

    @classmethod
    def to_client_model(cls, other: ContainerSpec) -> ChronosContainerSpec:
        params = None
        volumes = None
        if other.parameters:
            params = [
                ChronosContainerParameterSpecConverter.to_client_model(p)
                for p in other.parameters
            ]
        if other.volumes:
            volumes = [
                ChronosContainerVolumeSpecConverter.to_client_model(v)
                for v in other.volumes
            ]
        return ChronosContainerSpec(
            image=other.image,
            network=other.network,
            parameters=params,
            forcePullImage=other.pull_image,
            volumes=volumes,
        )


class ChronosEnvSpecConverter(
    ModelConverterInterface[EnvSpec, List[ChronosEnvSpec]]
):
    @classmethod
    def to_asgard_model(cls, other: List[ChronosEnvSpec]) -> EnvSpec:
        env_dict: EnvSpec = {}
        for other_item in other:
            env_dict[other_item.name] = other_item.value
        return env_dict

    @classmethod
    def to_client_model(cls, other: EnvSpec) -> List[ChronosEnvSpec]:
        return [
            ChronosEnvSpec(name=name, value=value)
            for name, value in other.items()
        ]


class ChronosFetchURLSpecConverter(
    ModelConverterInterface[List[FetchURLSpec], List[ChronosFetchURLSpec]]
):
    @classmethod
    def to_asgard_model(
        cls, other: List[ChronosFetchURLSpec]
    ) -> List[FetchURLSpec]:
        return [
            FetchURLSpec(
                type="ASGARD",
                uri=fetch_item.uri,
                executable=fetch_item.executable,
                cache=fetch_item.cache,
                extract=fetch_item.extract,
            )
            for fetch_item in other
        ]

    @classmethod
    def to_client_model(
        cls, other: List[FetchURLSpec]
    ) -> List[ChronosFetchURLSpec]:
        return [
            ChronosFetchURLSpec(
                uri=fetch_item.uri,
                executable=fetch_item.executable,
                cache=fetch_item.cache,
                extract=fetch_item.extract,
            )
            for fetch_item in other
        ]


class ChronosConstraintSpecConverter(
    ModelConverterInterface[ConstraintSpec, ChronosConstraintSpec]
):
    @classmethod
    def to_asgard_model(cls, other: ChronosConstraintSpec) -> ConstraintSpec:
        return [f"{item[0]}:{item[1]}:{item[2]}" for item in other]

    @classmethod
    def to_client_model(cls, other: ConstraintSpec) -> ChronosConstraintSpec:
        """
        As constraints do chronos são representadas como lista de lista. Cada constraint é uma lista de 3 elementos [<label>, <operador>, <valor>]. Aqui dividimos a contraint do Asgard em três, já que ela é representada como uma string "<label>:<operador>:<valor>"
        """
        constraint_spec: ChronosConstraintSpec = []
        for item in other:
            parts = item.split(":")
            constraint_spec.append([parts[0], parts[1], parts[2]])
        return constraint_spec
