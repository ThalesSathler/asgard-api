from asynctest import TestCase

from asgard.backends.chronos.models.converters import ChronosEnvSpecConverter
from asgard.clients.chronos.models.job import ChronosEnvSpec
from asgard.models.spec.env import EnvSpec


class ChronosEnvSpecConverterTest(TestCase):
    async def test_to_asgard_model(self):
        expected_asgard_env_dict = {"MY_ENV": "MY_VALUE"}
        chronos_env_spec = ChronosEnvSpec(name="MY_ENV", value="MY_VALUE")
        asgard_env_spec = ChronosEnvSpecConverter.to_asgard_model(
            [chronos_env_spec]
        )
        self.assertEqual(expected_asgard_env_dict, asgard_env_spec)

    async def test_to_asgard_model_multiple_envs(self):
        expected_asgard_env_dict = {
            "MY_ENV": "MY_VALUE",
            "OTHER_ENV": "OTHER_VALUE",
        }
        chronos_env_spec = [
            ChronosEnvSpec(name="MY_ENV", value="MY_VALUE"),
            ChronosEnvSpec(name="OTHER_ENV", value="OTHER_VALUE"),
        ]
        asgard_env_spec = ChronosEnvSpecConverter.to_asgard_model(
            chronos_env_spec
        )
        self.assertEqual(expected_asgard_env_dict, asgard_env_spec)

    async def test_to_client_model(self):
        asgarg_env_spec: EnvSpec = {"MY_ENV": "MY_VALUE"}
        chronos_env_spec = ChronosEnvSpecConverter.to_client_model(
            asgarg_env_spec
        )
        self.assertEqual(
            [{"name": "MY_ENV", "value": "MY_VALUE"}], chronos_env_spec
        )

    async def test_to_client_model_multiple_envs(self):
        asgarg_env_spec: EnvSpec = {
            "MY_ENV": "MY_VALUE",
            "OTHER_ENV": "OTHER_VALUE",
        }
        chronos_env_spec = ChronosEnvSpecConverter.to_client_model(
            asgarg_env_spec
        )
        self.assertEqual(
            [
                {"name": "MY_ENV", "value": "MY_VALUE"},
                {"name": "OTHER_ENV", "value": "OTHER_VALUE"},
            ],
            chronos_env_spec,
        )
