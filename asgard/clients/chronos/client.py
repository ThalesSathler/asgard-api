from base64 import b64encode
from typing import List, Optional

import aiohttp

from asgard.clients.chronos.models.job import ChronosJob
from asgard.http.client import HttpClient
from asgard.http.exceptions import HTTPNotFound, HTTPBadRequest


class ChronosClient:
    def __init__(
        self,
        url: str,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.client = HttpClient()
        self.address = url
        self.base_url = f"{self.address}/v1/scheduler"
        self.auth_data = None
        if user and password:
            auth_string = f"{user}:{password}"
            self.auth_data = b64encode(auth_string.encode("utf8")).decode(
                "utf8"
            )

    async def _request(
        self, method: str, url: str, **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Adiciona automaticamente a autenticação, caso user e password tenham
        sido passados no construtor do ChronosClient
        """
        if self.auth_data:
            kwargs["headers"] = {"Authorization": f"Basic {self.auth_data}"}
        return await getattr(self.client, method)(url, **kwargs)

    async def get_job_by_id(self, job_id: str) -> ChronosJob:
        """
        Retorna um Job do Chronos, dado seu id (nome).
        Raise asgard.http.exceptions.HTTPNotFound() se o job não existir
        """
        try:
            resp = await self._request(
                "get", f"{self.address}/v1/scheduler/job/{job_id}"
            )
        except HTTPBadRequest as e:
            # `/job/{name}` retorna 400 se o job não existe.
            # Isso acontece por causa dessa linha:
            # https://github.com/mesosphere/chronos/blob/7eff5e0e2d666a94bf240608a05afcbad5f2235f/src/main/scala/org/apache/mesos/chronos/scheduler/api/JobManagementResource.scala#L51
            raise HTTPNotFound(request_info=e.request_info)
        data = await resp.json()
        return ChronosJob(**data)

    async def search(self, name: str) -> List[ChronosJob]:
        """
        Procura por todos os jobs que contenham o termo `name` em seu nome.
        """
        resp = await self._request(
            "get",
            f"{self.address}/v1/scheduler/jobs/search",
            params={"name": name},
        )
        data = await resp.json()
        jobs = [ChronosJob(**job) for job in data]
        return jobs

    async def create_job(self, job: ChronosJob) -> ChronosJob:
        """
        O Chronos, pelo menos até a versão v3.0.2, tem um problema com jobs que usam timezone diferente de UTC.
        Quando colocamos, por exemplo, tz=America/Sao_Paulo o jobs fica programado para a hora certa, mas quando o momento
        chega o job fica com status OVERDUE mas *não roda*, nem aparece nos logs a tentativa de rodar o jobs.
        """
        await self._request("post", f"{self.base_url}/iso8601", json=job.dict())
        return job

    async def delete_job(self, job: ChronosJob) -> ChronosJob:
        await self._request("delete", f"{self.base_url}/job/{job.name}")
        return job
