from http import HTTPStatus
from typing import List

from asgard.clients.chronos.models.job import ChronosJob
from asgard.http.client import http_client
from asgard.http.exceptions import HTTPNotFound, HTTPBadRequest


class ChronosClient:
    def __init__(self, url: str) -> None:
        self.address = url
        self.base_url = f"{self.address}/v1/scheduler"

    async def get_job_by_id(self, job_id: str) -> ChronosJob:
        """
        Retorna um Job do Chronos, dado seu id (nome).
        Raise asgard.http.exceptions.HTTPNotFound() se o job não existir
        """
        async with http_client as client:
            resp = await client.get(f"{self.address}/v1/scheduler/job/{job_id}")
            if resp.status == HTTPStatus.BAD_REQUEST:
                # `/job/{name}` retorna 400 se o job não existe.
                # Isso acontece por causa dessa linha:
                # https://github.com/mesosphere/chronos/blob/7eff5e0e2d666a94bf240608a05afcbad5f2235f/src/main/scala/org/apache/mesos/chronos/scheduler/api/JobManagementResource.scala#L51
                raise HTTPNotFound()
            data = await resp.json()
            return ChronosJob(**data)

    async def search(self, name: str) -> List[ChronosJob]:
        """
        Procura por todos os jobs que contenham o termo `name` em seu nome.
        """
        async with http_client as client:
            resp = await client.get(
                f"{self.address}/v1/scheduler/jobs/search",
                params={"name": name},
            )
            data = await resp.json()
            jobs = [ChronosJob(**job) for job in data]
            return jobs

    async def create_job(self, job: ChronosJob) -> ChronosJob:
        async with http_client.post(
            f"{self.base_url}/iso8601", json=job.dict()
        ) as resp:
            resp.raise_for_status()
            return job

    async def delete_job(self, job: ChronosJob) -> ChronosJob:
        async with http_client.delete(
            f"{self.base_url}/job/{job.name}"
        ) as resp:
            if resp.status == HTTPStatus.BAD_REQUEST:
                raise HTTPBadRequest()
            return job
