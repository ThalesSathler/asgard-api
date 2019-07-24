from http import HTTPStatus

from asgard.clients.chronos.models.job import ChronosJob
from asgard.http.client import http_client
from asgard.http.exceptions import HTTPNotFound


class ChronosClient:
    def __init__(self, url: str) -> None:
        self.address = url

    async def get_job_by_id(self, job_id: str) -> ChronosJob:
        async with http_client as client:
            resp = await client.get(f"{self.address}/v1/scheduler/job/{job_id}")
            if resp.status == HTTPStatus.BAD_REQUEST:
                # `/job/{name}` retorna 400 se o job não existe.
                # Isso acontece por causa dessa linha:
                # https://github.com/mesosphere/chronos/blob/7eff5e0e2d666a94bf240608a05afcbad5f2235f/src/main/scala/org/apache/mesos/chronos/scheduler/api/JobManagementResource.scala#L51
                raise HTTPNotFound()
            data = await resp.json()
            return ChronosJob(**data)
