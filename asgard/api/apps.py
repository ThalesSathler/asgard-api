from aiohttp import web
from asyncworker import RouteTypes

from asgard.api.resources.apps import AppStatsResource
from asgard.app import app
from asgard.backends import mesos
from asgard.backends.base import Interval
from asgard.http.auth import auth_required
from asgard.models.account import Account
from asgard.models.user import User
from asgard.services.apps import AppsService


@app.route(
    ["/apps/{app_id:[.a-z0-9/-]+}/stats"], type=RouteTypes.HTTP, methods=["GET"]
)
@auth_required
async def app_stats(request: web.Request):
    app_id: str = request.match_info["app_id"]
    user = await User.from_alchemy_obj(request["user"])

    account = await Account.from_alchemy_obj(request["user"].current_account)
    stats = await AppsService.get_app_stats(
        app_id, Interval.ONE_HOUR, user, account, mesos
    )

    return web.json_response(AppStatsResource(stats=stats).dict())


@app.route(
    ["/apps/{app_id:[.a-z0-9/-]+}/stats/avg-1min"],
    type=RouteTypes.HTTP,
    methods=["GET"],
)
@auth_required
async def app_stats_avg_1min(request: web.Request):
    app_id: str = request.match_info["app_id"]
    user = await User.from_alchemy_obj(request["user"])

    account = await Account.from_alchemy_obj(request["user"].current_account)
    stats = await AppsService.get_app_stats(
        app_id, Interval.ONE_MINUTE, user, account, mesos
    )

    return web.json_response(AppStatsResource(stats=stats).dict())
