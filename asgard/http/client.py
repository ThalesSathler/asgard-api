from functools import wraps
from http import HTTPStatus
from typing import Optional, Dict, Any

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


class _HttpClient:
    _session: Optional[ClientSession]

    def __init__(
        self,
        session_class,
        url: str,
        method: str,
        session_class_args=[],
        session_class_kwargs={},
        *args,
        **kwargs,
    ) -> None:
        self._session = None
        self._session_class = session_class
        self._url = url
        self._args = args
        self._kwargs = kwargs
        self._method = method
        self._session_class_args = session_class_args
        self._session_class_kwargs = session_class_kwargs

    async def __aenter__(self):
        if not self._session:
            self._session = self._session_class(
                *self._session_class_args, **self._session_class_kwargs
            )
        return await self._return_session_method(self._session, self._method)(
            self._url, *self._args, **self._kwargs
        )

    def _return_session_method(self, session, method_name):
        return getattr(session, method_name.lower())

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self._session.close()


class _HttpClientMaker:
    def __init__(self, session_class, *args, **kwargs):
        self._session_class = session_class
        self.session = None
        self._session_class_args = args
        self._session_class_kwargs = kwargs

    def get(self, url: str, *args, **kwargs):
        return _HttpClient(
            self._session_class,
            url,
            "GET",
            self._session_class_args,
            self._session_class_kwargs,
            *args,
            **kwargs,
        )

    def post(self, url: str, *args, **kwargs):
        return _HttpClient(
            self._session_class,
            url,
            "POST",
            self._session_class_args,
            self._session_class_kwargs,
            *args,
            **kwargs,
        )

    def put(self, url: str, *args, **kwargs):
        return _HttpClient(
            self._session_class,
            url,
            "PUT",
            self._session_class_args,
            self._session_class_kwargs,
            *args,
            **kwargs,
        )

    def delete(self, url: str, *args, **kwargs):
        return _HttpClient(
            self._session_class,
            url,
            "DELETE",
            self._session_class_args,
            self._session_class_kwargs,
            *args,
            **kwargs,
        )

    async def __aenter__(self):
        if not self.session:
            self.session = self._session_class(
                timeout=default_http_client_timeout
            )
        return self.session

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None


http_client = _HttpClientMaker(
    ClientSession, timeout=default_http_client_timeout
)


class HttpClient:

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
        try:
            resp = await self._session.request(
                method,
                url,
                headers=headers,
                timeout=timeout,
                raise_for_status=raise_for_status,
                allow_redirects=True,
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
        return await self._request("get", url, **kwargs)

    async def post(self, url: str, **kwargs: Dict[str, Any]) -> ClientResponse:
        return await self._request("post", url, **kwargs)

    async def put(self, url: str, **kwargs: Dict[str, Any]) -> ClientResponse:
        return await self._request("put", url, **kwargs)

    async def patch(self, url: str, **kwargs: Dict[str, Any]) -> ClientResponse:
        return await self._request("patch", url, **kwargs)

    async def delete(
        self, url: str, **kwargs: Dict[str, Any]
    ) -> ClientResponse:
        return await self._request("delete", url, **kwargs)
