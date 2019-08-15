from aiohttp import RequestInfo
from aiohttp.web_exceptions import HTTPNotFound as AIOHTTPNotFound
from aiohttp.web_exceptions import HTTPBadRequest as AIOHTTPBadRequest
from aiohttp.web_exceptions import (
    HTTPInternalServerError as AIOHTTPInternalServerError,
)
from aiohttp.web_exceptions import HTTPException as AIOHTTPException


class HTTPException(AIOHTTPException):

    request_info: RequestInfo

    def __init__(self, request_info: RequestInfo) -> None:
        self.request_info = request_info

    @property
    def status(self) -> int:
        return self.status_code


class HTTPNotFound(HTTPException, AIOHTTPNotFound):
    pass


class HTTPInternalServerError(HTTPException, AIOHTTPInternalServerError):
    pass


class HTTPBadRequest(HTTPException, AIOHTTPBadRequest):
    pass
