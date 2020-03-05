from http import HTTPStatus
from json.decoder import JSONDecodeError

from aiohttp import web
from asyncworker import RouteTypes
from asyncworker.http.decorators import parse_path
from asyncworker.http.wrapper import RequestWrapper
from asyncworker.routes import call_http_handler
from pydantic import ValidationError

from asgard.api.resources import ErrorDetail, ErrorResource
from asgard.api.resources.jobs import (
    ScheduledJobResource,
    ScheduledJobsListResource,
    CreateScheduledJobResource,
)
from asgard.app import app
from asgard.backends.chronos.impl import ChronosScheduledJobsBackend
from asgard.exceptions import DuplicateEntity, NotFoundEntity
from asgard.http.auth import auth_required
from asgard.models.account import Account
from asgard.models.job import ScheduledJob
from asgard.models.user import User
from asgard.services.jobs import ScheduledJobsService


@app.route(["/jobs/{job_id}"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
@parse_path
async def index_jobs(job_id: str, user: User, account: Account):

    scheduled_job = await ScheduledJobsService.get_job_by_id(
        job_id, user, account, ChronosScheduledJobsBackend()
    )
    status_code = HTTPStatus.OK if scheduled_job else HTTPStatus.NOT_FOUND
    return web.json_response(
        ScheduledJobResource(job=scheduled_job).dict(), status=status_code
    )


@app.route(["/jobs"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def list_jobs(user: User, account: Account):

    jobs = await ScheduledJobsService.list_jobs(
        user, account, ChronosScheduledJobsBackend()
    )

    return web.json_response(ScheduledJobsListResource(jobs=jobs).dict())


def validate_input(handler):
    async def _wrapper(wrapper: RequestWrapper):
        try:
            req_body = await wrapper.http_request.json()
        except JSONDecodeError as e:
            return web.json_response(
                ErrorResource(errors=[ErrorDetail(msg=str(e))]).dict(),
                status=HTTPStatus.BAD_REQUEST,
            )

        try:
            job = ScheduledJob(**req_body)
        except ValidationError as e:
            return web.json_response(
                ErrorResource(errors=[ErrorDetail(msg=str(e))]).dict(),
                status=HTTPStatus.UNPROCESSABLE_ENTITY,
            )

        wrapper.types_registry.set(job)
        return await call_http_handler(wrapper.http_request, handler)

    return _wrapper


@app.route(["/jobs"], type=RouteTypes.HTTP, methods=["POST"])
@auth_required
@validate_input
async def create_job(job: ScheduledJob, user: User, account: Account):

    try:
        created_job = await ScheduledJobsService.create_job(
            job, user, account, ChronosScheduledJobsBackend()
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


async def _update_job(
    job: ScheduledJob, user: User, account: Account
) -> web.Response:
    try:
        updated_job = await ScheduledJobsService.update_job(
            job, user, account, ChronosScheduledJobsBackend()
        )
    except NotFoundEntity as e:
        return web.json_response(
            ErrorResource(errors=[ErrorDetail(msg=str(e))]).dict(),
            status=HTTPStatus.NOT_FOUND,
        )

    return web.json_response(
        CreateScheduledJobResource(job=updated_job).dict(),
        status=HTTPStatus.ACCEPTED,
    )


@app.route(["/jobs"], type=RouteTypes.HTTP, methods=["PUT"])
@auth_required
@validate_input
async def update_job(job: ScheduledJob, user: User, account: Account):
    return await _update_job(job, user, account)


@app.route(["/jobs/{job_id}"], type=RouteTypes.HTTP, methods=["PUT"])
@auth_required
@validate_input
@parse_path
async def update_job_by_id(
    job_id: str, job: ScheduledJob, user: User, account: Account
):
    job.id = job_id
    return await _update_job(job, user, account)


@app.route(["/jobs/{job_id}"], type=RouteTypes.HTTP, methods=["DELETE"])
@auth_required
@parse_path
async def delete_job(job_id: str, user: User, account: Account):
    scheduled_job = await ScheduledJobsService.get_job_by_id(
        job_id, user, account, ChronosScheduledJobsBackend()
    )
    status_code = HTTPStatus.OK if scheduled_job else HTTPStatus.NOT_FOUND
    if scheduled_job:
        await ScheduledJobsService.delete_job(
            scheduled_job, user, account, ChronosScheduledJobsBackend()
        )
    return web.json_response(
        ScheduledJobResource(job=scheduled_job).dict(), status=status_code
    )
