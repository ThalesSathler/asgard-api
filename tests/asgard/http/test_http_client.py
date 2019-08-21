from http import HTTPStatus

from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ClientResponseError
from aioresponses import aioresponses
from asynctest import TestCase
from asynctest.mock import CoroutineMock, Mock, ANY
from yarl import URL

from asgard.http.client import default_http_client_timeout, HttpClient
from asgard.http.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
    HTTPBadRequest,
)

TEST_URL = "http://server.com"


class HttpClientTest(TestCase):
    async def setUp(self):
        self.session_mock = CoroutineMock(
            post=CoroutineMock(),
            put=CoroutineMock(),
            delete=CoroutineMock(),
            get=CoroutineMock(),
            close=CoroutineMock(),
            request=CoroutineMock(),
        )
        self.session_class_mock = Mock(return_value=self.session_mock)

    async def test_reuse_session_on_subsequent_requests(self):
        client = HttpClient()
        with aioresponses() as rsps:
            rsps.get(TEST_URL, status=200)
            rsps.get(TEST_URL, status=200)

            await client.get(TEST_URL)

            client_session = client._session

            await client.get(TEST_URL)

            self.assertTrue(client_session is client._session)

    async def test_can_merge_default_headers_with_headers_passed_on_the_request_real_request(
        self
    ):
        """
        O aioresponses não funciona quando usamos default_headers no ClientSession.
        """
        default_headers = {"X-Header": "Value"}
        additional_headers = {"X-More": "Other"}

        client = HttpClient(headers=default_headers)
        resp = await client.get(
            "https://httpbin.org/headers", headers=additional_headers
        )
        self.assertEqual(HTTPStatus.OK, resp.status)

        resp_data = await resp.json()
        self.assertEqual("Value", resp_data["headers"].get("X-Header"))
        self.assertEqual("Other", resp_data["headers"].get("X-More"))

    async def test_headers_passed_on_the_request_ovewrites_default_headers(
        self
    ):
        """
        Se um header passado em `client.get(..., headers={})` tiver o mesmo nome de um
        outro header passado na instanciação do http client, o header do request
        deve ser usado
        """
        default_headers = {"X-Header": "Value"}
        additional_headers = {"X-More": "Other", "X-Header": "Override"}

        client = HttpClient(headers=default_headers)
        with aioresponses() as rsps:
            rsps.get(TEST_URL, status=200)
            resp = await client.get(TEST_URL, headers=additional_headers)
            self.assertEqual(HTTPStatus.OK, resp.status)

            req = rsps.requests.get(("get", URL(TEST_URL)))
            expected_headers = {**additional_headers}
            self.assertEqual(expected_headers, req[0].kwargs.get("headers"))

    async def test_client_always_has_default_timeout_configured(self):

        client = HttpClient()
        client.session_class = self.session_class_mock

        await client.get(TEST_URL)

        client.session_class.assert_called_with(
            timeout=default_http_client_timeout,
            headers=ANY,
            raise_for_status=True,
        )

    async def test_can_choose_a_different_timeout_on_client_instantiation(self):
        new_timeout = ClientTimeout(total=2, connect=5)
        client = HttpClient(timeout=new_timeout)
        client.session_class = self.session_class_mock

        await client.get(TEST_URL)

        client.session_class.assert_called_with(
            timeout=new_timeout, headers=ANY, raise_for_status=True
        )

        client._session.request.assert_awaited_with(
            "get",
            ANY,
            timeout=None,
            headers=ANY,
            allow_redirects=True,
            raise_for_status=True,
        )

    async def test_can_override_timeout_passing_a_new_timeout_on_the_request(
        self
    ):
        """
        client.get(..., timeout=ClientTimeout(...))
        """
        timeout = ClientTimeout(connect=1, total=5)
        client = HttpClient()
        client.session_class = self.session_class_mock

        await client.get(TEST_URL, timeout=timeout)
        client._session.request.assert_awaited_with(
            "get",
            ANY,
            timeout=timeout,
            headers=ANY,
            allow_redirects=True,
            raise_for_status=True,
        )

    async def test_can_override_option_to_automatically_raise_when_request_fails(
        self
    ):
        timeout = ClientTimeout(connect=1, total=5)
        client = HttpClient()
        client.session_class = self.session_class_mock

        await client.get(TEST_URL, raise_for_status=False)
        client._session.request.assert_awaited_with(
            "get",
            ANY,
            timeout=ANY,
            headers=ANY,
            raise_for_status=False,
            allow_redirects=True,
        )

    async def test_exceptions_have_detail_info_about_the_request_that_failed(
        self
    ):
        """
        Cada exceção lançada deve carregar algumas infos sobre o request original.
        A ClientResponseError da aiohttp tem tudo que queremos.

        A exception lançada pelo client contém:
          - request_info original
          - status (int)
        """
        client = HttpClient()
        url = "https://httpbin.org/status/404"

        try:
            await client.get(url)
        except HTTPNotFound as e:
            self.assertEqual(HTTPStatus.NOT_FOUND, e.status)
            self.assertEqual(url, str(e.request_info.url))
            self.assertEqual("GET", e.request_info.method)
            self.assertIsNotNone(e.request_info.headers)

    async def test_raise_internal_error_exception_when_response_is_500(self):
        client = HttpClient()
        url = "https://httpbin.org/status/500"

        try:
            await client.get(url)
        except HTTPInternalServerError as e:
            self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, e.status)
            self.assertEqual(url, str(e.request_info.url))
            self.assertEqual("GET", e.request_info.method)
            self.assertIsNotNone(e.request_info.headers)

    async def test_raise_bad_request_exception_when_response_is_400(self):
        client = HttpClient()
        url = "https://httpbin.org/status/400"

        try:
            await client.get(url)
        except HTTPBadRequest as e:
            self.assertEqual(HTTPStatus.BAD_REQUEST, e.status)
            self.assertEqual(url, str(e.request_info.url))
            self.assertEqual("GET", e.request_info.method)
            self.assertIsNotNone(e.request_info.headers)

    async def test_re_raise_original_exception(self):
        """
        Se o request lançar uma exception que não estamos tratando, devemos re-lançar.
        """
        client = HttpClient()
        url = "https://httpbin.org/status/415"

        try:
            await client.get(url)
        except ClientResponseError as e:
            self.assertEqual(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, e.status)
            self.assertEqual(url, str(e.request_info.url))
            self.assertEqual("GET", e.request_info.method)
            self.assertIsNotNone(e.request_info.headers)

    async def test_always_make_request_with_follow_redirect(self):
        """
        Seguimos redirect por padrão
        """
        client = HttpClient()
        client.session_class = self.session_class_mock

        await client.get(TEST_URL)
        client._session.request.assert_called_with(
            "get",
            TEST_URL,
            timeout=ANY,
            headers=ANY,
            allow_redirects=True,
            raise_for_status=True,
        )

    async def test_post(self):
        expected_headers = {"X-Header": "Value"}
        timeout = ClientTimeout(connect=5, total=10)
        client = HttpClient()
        client.session_class = self.session_class_mock

        await client.post(TEST_URL, timeout=timeout, headers=expected_headers)
        client._session.request.assert_awaited_with(
            "post",
            TEST_URL,
            timeout=timeout,
            headers=expected_headers,
            raise_for_status=True,
            allow_redirects=True,
        )

    async def test_get(self):
        expected_headers = {"X-Header": "Value"}
        timeout = ClientTimeout(connect=5, total=10)
        client = HttpClient()
        client.session_class = self.session_class_mock

        await client.get(TEST_URL, timeout=timeout, headers=expected_headers)
        client._session.request.assert_awaited_with(
            "get",
            TEST_URL,
            timeout=timeout,
            headers=expected_headers,
            raise_for_status=True,
            allow_redirects=True,
        )

    async def test_put(self):
        expected_headers = {"X-Header": "Value"}
        timeout = ClientTimeout(connect=5, total=10)
        client = HttpClient()
        client.session_class = self.session_class_mock

        await client.put(TEST_URL, timeout=timeout, headers=expected_headers)
        client._session.request.assert_awaited_with(
            "put",
            TEST_URL,
            timeout=timeout,
            headers=expected_headers,
            raise_for_status=True,
            allow_redirects=True,
        )

    async def test_patch(self):
        expected_headers = {"X-Header": "Value"}
        timeout = ClientTimeout(connect=5, total=10)
        client = HttpClient()
        client.session_class = self.session_class_mock

        await client.patch(TEST_URL, timeout=timeout, headers=expected_headers)
        client._session.request.assert_awaited_with(
            "patch",
            TEST_URL,
            timeout=timeout,
            headers=expected_headers,
            raise_for_status=True,
            allow_redirects=True,
        )

    async def test_delete(self):
        expected_headers = {"X-Header": "Value"}
        timeout = ClientTimeout(connect=5, total=10)
        client = HttpClient()
        client.session_class = self.session_class_mock

        await client.delete(TEST_URL, timeout=timeout, headers=expected_headers)
        client._session.request.assert_awaited_with(
            "delete",
            TEST_URL,
            timeout=timeout,
            headers=expected_headers,
            raise_for_status=True,
            allow_redirects=True,
        )

    async def test_can_pass_extra_kwarg_to_aiohttp_client_sesson(self):
        """
        Confirmamos que quando passamos argumentos extras para o HttpClient
        isso é repassado para o ClientSession
        """
        client = HttpClient()
        client.session_class = self.session_class_mock

        await client.put(TEST_URL, json={"key": "value"})
        client._session.request.assert_awaited_with(
            "put",
            TEST_URL,
            timeout=None,
            headers={},
            raise_for_status=True,
            allow_redirects=True,
            json={"key": "value"},
        )
