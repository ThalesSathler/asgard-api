from http import HTTPStatus
from json.decoder import JSONDecodeError

from aiohttp import web
from asyncworker import RouteTypes
from pydantic import ValidationError

from asgard.api.resources import ErrorDetail, ErrorResource
from asgard.api.resources.jobs import (
    ScheduledJobResource,
    ScheduledJobsListResource,
    CreateScheduledJobResource,
)
from asgard.app import app
from asgard.backends.chronos.impl import ChronosScheduledJobsBackend
from asgard.exceptions import DuplicateEntity
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


@app.route(["/jobs"], type=RouteTypes.HTTP, methods=["POST"])
@auth_required
async def create_job(request: web.Request):
    user = await User.from_alchemy_obj(request["user"])
    account = await Account.from_alchemy_obj(request["user"].current_account)

    try:
        req_body = await request.json()
    except JSONDecodeError as e:
        return web.json_response(
            ErrorResource(errors=[ErrorDetail(msg=str(e))]).dict(),
            status=HTTPStatus.BAD_REQUEST,
        )

    try:
        asgard_job = ScheduledJob(**req_body)
    except ValidationError as e:
        return web.json_response(
            ErrorResource(errors=[ErrorDetail(msg=str(e))]).dict(),
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    try:
        created_job = await ScheduledJobsService.create_job(
            asgard_job, user, account, ChronosScheduledJobsBackend()
        )
    except DuplicateEntity as e:
        return web.json_response(
            ErrorResource(errors=[ErrorDetail(msg=str(e))]).dict(),
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
    return web.json_response(
        CreateScheduledJobResource(job=created_job).dict(),
        status=HTTPStatus.CREATED,
    )
