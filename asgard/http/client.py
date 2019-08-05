from typing import Optional, Union

from aiohttp import ClientSession, ClientTimeout  # type: ignore

from asgard import conf

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
