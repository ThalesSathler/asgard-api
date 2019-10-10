from http import HTTPStatus

from aiohttp import web, ClientSession
from asynctest import TestCase
from asyncworker import RouteTypes, App
from asyncworker.conf import settings

from asgard.app import patched_startup


class PatchedStartupAppTest(TestCase):
    async def test_patched_startup_has_cors_configured(self):

        app = App()
        app._on_startup.clear()
        app._on_startup.append(patched_startup)

        @app.route(["/new-path"], type=RouteTypes.HTTP, methods=["GET"])
        async def handler(r):
            return web.json_response({})

        client = ClientSession()
        await app.startup()
        resp = await client.get(
            f"http://{settings.HTTP_HOST}:{settings.HTTP_PORT}/new-path",
            headers={"Origin": "server.com"},
        )
        self.assertEqual(HTTPStatus.OK, resp.status)

        self.assertTrue(
            "Access-Control-Allow-Origin" in resp.headers,
            "Header do CORS não encontrado",
        )
        self.assertEqual(
            "server.com", resp.headers.get("Access-Control-Allow-Origin")
        )
        await app.shutdown()

    async def test_patched_startup_app_without_routes(self):
        app = App()
        app._on_startup.clear()
        app._on_startup.append(patched_startup)

        client = ClientSession()
        await app.startup()
        resp = await client.get(
            f"http://{settings.HTTP_HOST}:{settings.HTTP_PORT}/new-path",
            headers={"Origin": "server.com"},
        )
        self.assertEqual(HTTPStatus.NOT_FOUND, resp.status)

        self.assertFalse("Access-Control-Allow-Origin" in resp.headers)
        await app.shutdown()
