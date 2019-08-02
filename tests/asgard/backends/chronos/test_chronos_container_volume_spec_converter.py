from asynctest import TestCase

from asgard.backends.chronos.models.converters import (
    ChronosContainerVolumeSpecConverter,
)
from asgard.clients.chronos.models.job import ChronosContainerVolumeSpec
from asgard.models.spec.container import (
    ContainerVolumeSpec,
    ContainerVolumeModeSpec,
)


class ChronosContainerVolumeSpecConverterTest(TestCase):
    async def test_to_asgard_model(self):
        chronos_volume_spec = ChronosContainerVolumeSpec(
            containerPath="/var/data", hostPath="/tmp", mode="RW"
        )
        asgard_volume_spec = ChronosContainerVolumeSpecConverter.to_asgard_model(
            chronos_volume_spec
        )
        self.assertEqual(
            {
                "container_path": "/var/data",
                "host_path": "/tmp",
                "mode": "RW",
                "persistent": False,
                "external": False,
            },
            asgard_volume_spec.dict(),
        )

    async def test_to_client_model(self):
        asgard_volume_spec = ContainerVolumeSpec(
            container_path="/var/data",
            host_path="/tmp",
            mode=ContainerVolumeModeSpec.RO,
        )
        chronos_volume_spec = ChronosContainerVolumeSpecConverter.to_client_model(
            asgard_volume_spec
        )
        self.assertEqual(
            {"hostPath": "/tmp", "containerPath": "/var/data", "mode": "RO"},
            chronos_volume_spec.dict(),
        )
