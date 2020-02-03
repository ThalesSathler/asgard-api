# encoding: utf-8

import json
import os
import sys
import traceback
from datetime import timedelta

import marathon
import newrelic.agent
from flask import Response, request
from flask_cors import CORS

from hollowman import cache
from hollowman.api.account import account_blueprint
from hollowman.api.tasks import tasks_blueprint
from hollowman.auth.jwt import jwt_auth
from hollowman.conf import (
    CORS_WHITELIST,
    NEW_RELIC_APP_NAME,
    NEW_RELIC_LICENSE_KEY,
    SECRET_KEY,
)
from hollowman.hollowman_flask import HollowmanFlask
from hollowman.log import dev_null_logger, logger
from hollowman.plugins import load_all_metrics_plugins, register_plugin
from hollowman.routes import all_routes

if NEW_RELIC_LICENSE_KEY and NEW_RELIC_APP_NAME:
    newrelic.agent.initialize()

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
STATIC_FILE_PATH = os.path.normpath(os.path.join(PROJECT_ROOT, "../static"))

application = HollowmanFlask(
    __name__, static_url_path="/static", static_folder=STATIC_FILE_PATH
)
application.url_map.strict_slashes = False
application.secret_key = SECRET_KEY
application.permanent_session_lifetime = timedelta(minutes=5)
application.config["JWT_AUTH_URL_RULE"] = None
application.config["JWT_EXPIRATION_DELTA"] = timedelta(days=7)

application.register_blueprint(all_routes, url_prefix="")
application.register_blueprint(account_blueprint, url_prefix="/hollow/account")
application.register_blueprint(tasks_blueprint, url_prefix="/tasks")

CORS(application, origins=CORS_WHITELIST)
jwt_auth.init_app(application)
cache.init_app(application)


def _get_current_exception_if_exists(current_request):
    try:
        return current_request.current_exception
    except Exception as e:
        return None


@application.after_request
def after_request(response):
    logger.info(
        {
            "method": request.method,
            "status_code": response.status_code,
            "path": request.path,
            "user": (hasattr(request, "user") and request.user.tx_email)
            or None,
            "account_id": (
                hasattr(request, "user") and request.user.current_account.id
            )
            or None,
            "location": response.headers.get("Location"),
            "user-agent": request.headers.get("User-Agent"),
            "qstring": request.args,
            "current_exception": _get_current_exception_if_exists(request),
        }
    )
    return response


@application.errorhandler(Exception)
def handler_500(error):
    current_exception = {
        "message": str(error),
        "traceback": traceback.format_exc(),
        "type": sys.exc_info()[0].__name__,
    }
    request.current_exception = current_exception

    return Response(response=json.dumps(current_exception), status=500)


marathon.log = dev_null_logger


register_plugin("example-plugin")
register_plugin("session-checker-plugin")
load_all_metrics_plugins(application)
