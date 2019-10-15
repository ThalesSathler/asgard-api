import aiohttp_cors
from aiohttp import web
from asyncworker import App, RouteTypes
from asyncworker.conf import settings
from asyncworker.connections import AMQPConnection

from asgard import conf

conn = AMQPConnection(
    hostname=conf.ASGARD_RABBITMQ_HOST,
    username=conf.ASGARD_RABBITMQ_USER,
    password=conf.ASGARD_RABBITMQ_PASS,
    prefetch=conf.ASGARD_RABBITMQ_PREFETCH,
)

app = App(connections=[conn])


async def patched_startup(app):

    app[RouteTypes.HTTP] = {}
    routes = app.routes_registry.http_routes

    app[RouteTypes.HTTP]["app"] = http_app = web.Application()
    for route in routes:
        for route_def in route.aiohttp_routes():
            route_def.register(http_app.router)

    cors = aiohttp_cors.setup(
        http_app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True, expose_headers="*", allow_headers="*"
            )
        },
    )

    # Configure CORS on all routes.
    for route in list(http_app.router.routes()):
        cors.add(route)

    app[RouteTypes.HTTP]["runner"] = web.AppRunner(http_app)
    await app[RouteTypes.HTTP]["runner"].setup()
    app[RouteTypes.HTTP]["site"] = web.TCPSite(
        runner=app[RouteTypes.HTTP]["runner"],
        host=settings.HTTP_HOST,
        port=settings.HTTP_PORT,
    )

    await app[RouteTypes.HTTP]["site"].start()


app._on_startup.clear()
app._on_startup.append(patched_startup)
