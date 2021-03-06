from typing import List

from aiohttp.web import json_response
from asyncworker import RouteTypes

from asgard.api.resources.users import UserResource
from asgard.app import app
from asgard.backends.users import UsersBackend
from asgard.http.auth import auth_required
from asgard.http.auth.auth_required import _get_account_by_id
from asgard.models.account import Account
from asgard.models.user import User
from asgard.services.users import UsersService


@app.route(["/users/me"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def whoami(request):
    user = await User.from_alchemy_obj(request.user)
    current_account = await Account.from_alchemy_obj(
        request.user.current_account
    )

    alternate_accounts = await UsersService.get_alternate_accounts(
        user, current_account, UsersBackend()
    )

    resource_response = UserResource(
        user=user, current_account=current_account, accounts=alternate_accounts
    )

    return json_response(resource_response.dict())
