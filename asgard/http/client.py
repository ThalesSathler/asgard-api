from functools import wraps
from http import HTTPStatus
from typing import Dict, Any

from aiohttp import ClientSession, ClientTimeout, ClientResponse  # type: ignore
from aiohttp.client_exceptions import ClientResponseError

from asgard import conf
from asgard.http.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
    HTTPBadRequest,
)

default_http_client_timeout = ClientTimeout(
    total=conf.ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT,
    connect=conf.ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT,
)


class HttpClient:
    """
    Wrapper em volta do objeto aiohttp.ClientSession. Possui a seguintes features:

    - Já lança exception em caso de response ``4xx`` e ``5xx``. Esse comportamento pode ser sobrescrito, a cada request, passando o argumento ``raise_for_status=True``.
    - Já segue redirect dos requests. 
    - Headers que podem ser passados ao instanciar um objeto HttpClient
        - Esses headers serão mesclados com quaisquer outros headers que forem passados no momento em que um request HTTP for feito.
        - Em caso de headers de nomes iguais, os headers passados ao request terão maior precedência
    - Timeout já configurado. Se nada for passado no construtor um timeout padrão já estará configurado. Esse timeout tem seus valores nas configs: :py:const:`asgard.conf.ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT` e :py:const:`asgard.conf.ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT`. Esses valores podem ser sobrescritos com as envs ``ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT`` e ``ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT``.
    """

    _session: ClientSession

    def __init__(
        self,
        headers: Dict[str, str] = {},
        timeout: ClientTimeout = default_http_client_timeout,
    ) -> None:
        self.default_headers = headers
        self.session_class = ClientSession
        self.timeout = timeout

    def _ensure_session(fn):
        @wraps(fn)
        async def _handler(self, *args, **kwargs):
            try:
                self._session
            except AttributeError:
                self._session = self.session_class(
                    headers=self.default_headers,
                    timeout=self.timeout,
                    raise_for_status=True,
                )

            return await fn(self, *args, **kwargs)

        return _handler

    @_ensure_session
    async def _request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str] = {},
        timeout: ClientTimeout = None,
        raise_for_status: bool = True,
        **kwargs: Dict[str, Any],
    ) -> ClientResponse:
        """
        Método que é usado por todos os outros métodos para fazer um request.
        O parametros recebidos por esse métodos definem os parametros recebidos pelo client de uma forma geral.
        """
        try:
            resp = await self._session.request(
                method,
                url,
                headers=headers,
                timeout=timeout,
                raise_for_status=raise_for_status,
                allow_redirects=True,
                **kwargs,
            )
        except ClientResponseError as ce:
            if ce.status == HTTPStatus.NOT_FOUND:
                raise HTTPNotFound(request_info=ce.request_info)
            if ce.status == HTTPStatus.INTERNAL_SERVER_ERROR:
                raise HTTPInternalServerError(request_info=ce.request_info)
            if ce.status == HTTPStatus.BAD_REQUEST:
                raise HTTPBadRequest(request_info=ce.request_info)
            raise ce

        return resp

    async def get(self, url: str, **kwargs: Dict[str, Any]) -> ClientResponse:
        """
        Alias coroutine para GET <url>
        """
        return await self._request("get", url, **kwargs)

    async def post(self, url: str, **kwargs: Dict[str, Any]) -> ClientResponse:
        """
        Alias coroutine para POST <url>
        """
        return await self._request("post", url, **kwargs)

    async def put(self, url: str, **kwargs: Dict[str, Any]) -> ClientResponse:
        """
        Alias coroutine para PUT <url>
        """
        return await self._request("put", url, **kwargs)

    async def patch(self, url: str, **kwargs: Dict[str, Any]) -> ClientResponse:
        """
        Alias coroutine para PATCH <url>
        """
        return await self._request("patch", url, **kwargs)

    async def delete(
        self, url: str, **kwargs: Dict[str, Any]
    ) -> ClientResponse:
        """
        Alias coroutine para DELETE <url>
        """
        return await self._request("delete", url, **kwargs)
