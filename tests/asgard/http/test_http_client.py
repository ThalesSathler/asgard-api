import asynctest
from asynctest.mock import CoroutineMock, Mock

from asgard.http.client import (
    _HttpClient,
    _HttpClientMaker,
    default_http_client_timeout,
)


class HttpClientTest(asynctest.TestCase):
    async def setUp(self):
        self._session_mock = CoroutineMock(
            post=CoroutineMock(),
            put=CoroutineMock(),
            delete=CoroutineMock(),
            get=CoroutineMock(),
            close=CoroutineMock(),
        )
        self.session_class_mock = Mock(return_value=self._session_mock)

    async def test_calls_apropriate_method_on_shared_session(self):
        client = _HttpClient(
            self.session_class_mock, "https://httpbin.org/ip", "POST"
        )
        async with client:
            self.session_class_mock.assert_called_with()
            client._session.post.assert_awaited_with("https://httpbin.org/ip")

    async def test_close_shared_session_on_context_exit(self):
        client = _HttpClient(
            self.session_class_mock, "https://httpbin.org/ip", "POST"
        )
        async with client:
            self.session_class_mock.assert_called_with()
            client._session.close.assert_not_awaited()
        client._session.close.assert_awaited_with()


class HttpClientMkakerTest(asynctest.TestCase):
    async def setUp(self):
        self._session_mock = CoroutineMock(
            post=CoroutineMock(),
            put=CoroutineMock(),
            delete=CoroutineMock(),
            get=CoroutineMock(),
            close=CoroutineMock(),
        )
        self.session_class_mock = Mock(return_value=self._session_mock)
        self.url = "https://httpbin.org/ip"

    async def test_different_args_kwargs_for_session_and_client_get(self):
        """
        Devemos ter args/kwargs distintos para a ClientSession e para
        o http_client final (get/post/etc)
        Por exemplo: Tanto a SessionClass quanto o client recebem `timeout` com kwargs,
        mas apenas o client recebe `allow_redirects`, por exemplo.

        Atualmente os args/kwargs passados para o client (get/post/etc) estão sendo repassados
        para criar a ClientSession, isso impede de usar o client dessa forma:
            async with http_client.get(URL, allow_redirects=False) as response:
                ...
        """
        client_maker = _HttpClientMaker(
            self.session_class_mock, 10, 30, param1=42, param2=60
        )
        async with client_maker.get(
            self.url, allow_redirects=False
        ) as response:
            self.session_class_mock.assert_called_with(
                10, 30, param1=42, param2=60
            )
            self._session_mock.get.assert_awaited_with(
                self.url, allow_redirects=False
            )

    async def test_different_args_kwargs_for_session_and_client_post(self):
        client_maker = _HttpClientMaker(
            self.session_class_mock, 10, 30, param1=42, param2=60
        )
        async with client_maker.post(
            self.url, allow_redirects=False
        ) as response:
            self.session_class_mock.assert_called_with(
                10, 30, param1=42, param2=60
            )
            self._session_mock.post.assert_awaited_with(
                self.url, allow_redirects=False
            )

    async def test_different_args_kwargs_for_session_and_client_put(self):
        client_maker = _HttpClientMaker(
            self.session_class_mock, 10, 30, param1=42, param2=60
        )
        async with client_maker.put(
            self.url, allow_redirects=False
        ) as response:
            self.session_class_mock.assert_called_with(
                10, 30, param1=42, param2=60
            )
            self._session_mock.put.assert_awaited_with(
                self.url, allow_redirects=False
            )

    async def test_different_args_kwargs_for_session_and_client_delete(self):
        client_maker = _HttpClientMaker(
            self.session_class_mock, 10, 30, param1=42, param2=60
        )
        async with client_maker.delete(
            self.url, allow_redirects=False
        ) as response:
            self.session_class_mock.assert_called_with(
                10, 30, param1=42, param2=60
            )
            self._session_mock.delete.assert_awaited_with(
                self.url, allow_redirects=False
            )

    async def test_uses_default_timeout_configs(self):
        self.assertEqual(default_http_client_timeout.connect, 1)
        self.assertEqual(default_http_client_timeout.total, 30)

    async def test_with_block_on_client_return_session(self):
        session_class = Mock(return_value=self._session_mock)
        client_maker = _HttpClientMaker(session_class)

        async with client_maker as session:
            self.assertEqual(session, self._session_mock)

    async def test_reuse_session(self):
        session_class = Mock(return_value=self._session_mock)
        client_maker = _HttpClientMaker(session_class)

        async with client_maker as session1:
            async with client_maker as session2:
                self.assertEqual(session1, self._session_mock)
                self.assertEqual(session2, self._session_mock)
                session_class.assert_called_once()

    async def test_shared_session_must_be_closed_on_context_exit(self):
        """
        Se não fechamos a sessão, caso o loop seja trocado, o http_client
        que já foi usado antes (e por isso já tem uma session aberta) para
        de funcionar com o erro "loop is closed".

        O que temos que fazer é melhorar a API desse http_client. Idealmente
        exigino que ele seja instanciado antes de ser usado.
        Em vez de fazermos assim:
        from asgard.http.client import http_client

        async with http_client as client:
          await client.get(...)

        Fazer algo nessa linha:
        from asgard.http.client import HttpClient

        client = HttpClient(headers=..., ...)
        await client.get(...)
        """
        client = _HttpClientMaker(self.session_class_mock)
        original_session = None
        async with client:
            self.session_class_mock.assert_called_with(
                timeout=default_http_client_timeout
            )
            client.session.close.assert_not_awaited()
            original_session = client.session
        original_session.close.assert_awaited()
        self.assertIsNone(client.session)

    async def test_call_session_with_default_timeout_settings(self):
        session_class = Mock(return_value=self._session_mock)
        client_maker = _HttpClientMaker(session_class)

        async with client_maker as session:
            pass
        session_class.assert_called_with(timeout=default_http_client_timeout)
