from http import HTTPStatus

from aiohttp import web
from asyncworker import RouteTypes

from asgard.api.resources.jobs import (
    ScheduledJobResource,
    ScheduledJobsListResource,
)
from asgard.app import app
from asgard.backends.chronos.impl import ChronosScheduledJobsBackend
from asgard.http.auth import auth_required
from asgard.models.account import Account
from asgard.models.job import ScheduledJob
from asgard.models.user import User
from asgard.services.jobs import ScheduledJobsService


@app.route(["/jobs/{job_id}"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def index_jobs(request: web.Request):
    user = await User.from_alchemy_obj(request["user"])
    account = await Account.from_alchemy_obj(request["user"].current_account)
    job_id = request.match_info["job_id"]

    scheduled_job = await ScheduledJobsService.get_job_by_id(
        job_id, user, account, ChronosScheduledJobsBackend()
    )
    status_code = HTTPStatus.OK if scheduled_job else HTTPStatus.NOT_FOUND
    return web.json_response(
        ScheduledJobResource(job=scheduled_job).dict(), status=status_code
    )


@app.route(["/jobs"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def list_jobs(request: web.Request):
    user = await User.from_alchemy_obj(request["user"])
    account = await Account.from_alchemy_obj(request["user"].current_account)

    jobs = await ScheduledJobsService.list_jobs(
        user, account, ChronosScheduledJobsBackend()
    )

    return web.json_response(ScheduledJobsListResource(jobs=jobs).dict())
