from asynctest import TestCase

from asgard.backends.chronos.models.converters import (
    ChronosFetchURLSpecConverter,
)
from asgard.clients.chronos.models.job import ChronosFetchURLSpec
from asgard.models.spec.fetch import FetchURLSpec
from tests.utils import with_json_fixture


class ChronosFetchURLSpecConverterTest(TestCase):
    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_to_asgard_model_multiple_fetch(self, chronos_job_fixture):
        chronos_fetch_list = chronos_job_fixture["fetch"]
        chronos_fetch_url_spec = [
            ChronosFetchURLSpec(**chronos_fetch_list[0]),
            ChronosFetchURLSpec(**chronos_fetch_list[1]),
        ]
        asgard_fetch_url_spec = ChronosFetchURLSpecConverter.to_asgard_model(
            chronos_fetch_url_spec
        )
        self.assertEqual(
            [
                {
                    "uri": chronos_fetch_list[0]["uri"],
                    "executable": False,
                    "extract": True,
                    "cache": False,
                },
                {
                    "uri": chronos_fetch_list[1]["uri"],
                    "executable": False,
                    "extract": False,
                    "cache": False,
                },
            ],
            [asgard_fetch_url_spec[0].dict(), asgard_fetch_url_spec[1].dict()],
        )

    async def test_to_client_model(self):
        base_fetch_list = [
            {
                "uri": "https://static.server.com/file.bz2",
                "executable": False,
                "extract": True,
                "cache": False,
            },
            {
                "uri": "https://static.server.com/file.txt",
                "executable": False,
                "extract": False,
                "cache": False,
            },
        ]

        expected_chronos_fetch_list = [
            {"type": "CHRONOS", **base_fetch_list[0]},
            {"type": "CHRONOS", **base_fetch_list[1]},
        ]

        expected_asgard_fetch_list = [
            {**base_fetch_list[0]},
            {**base_fetch_list[1]},
        ]

        asgard_fetch_list = [
            FetchURLSpec(**expected_asgard_fetch_list[0]),
            FetchURLSpec(**expected_asgard_fetch_list[1]),
        ]
        chronos_fetch_list = ChronosFetchURLSpecConverter.to_client_model(
            asgard_fetch_list
        )
        self.assertEqual(
            expected_chronos_fetch_list,
            [chronos_fetch_list[0].dict(), chronos_fetch_list[1].dict()],
        )
