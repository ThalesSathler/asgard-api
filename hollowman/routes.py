#encoding: utf-8

import requests
from flask import Flask, url_for, redirect, Response, request, session, render_template, make_response
import json

from hollowman import conf
from hollowman import upstream
from hollowman.app import application
from hollowman.auth.google import google_oauth2
from hollowman.decorators import populate_user
from hollowman.filters.request import RequestFilter
from hollowman.log import logger
from hollowman.auth.jwt import jwt_auth
from hollowman.plugins import PLUGIN_REGISTRY, get_plugin_registry_data

@application.route("/", methods=["GET"])
def index():
    return Response(status=302, headers={"Location": conf.REDIRECT_ROOTPATH_TO})

@application.route('/v2', defaults={'path': '/'})
@application.route('/v2/', defaults={'path': ''})
@application.route('/v2/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
@populate_user()
def apiv2(path):
    modded_request = request
    try:
        modded_request = RequestFilter.dispatch(request)
    except Exception as e:
        import traceback
        traceback.print_exc()
    r = upstream.replay_request(modded_request, conf.MARATHON_ENDPOINT)
    h = dict(r.headers)
    h.pop("Transfer-Encoding", None)
    return Response(response=r.content, status=r.status_code, headers=h)

@application.route("/healthcheck")
@populate_user()
def healhcheck():
    r = requests.get(conf.MARATHON_ENDPOINT, headers={"Authorization": conf.MARATHON_AUTH_HEADER})
    return Response(response="", status=r.status_code)

@application.route("/login/google")
def google_login():
    callback=url_for("authorized", _external=True)
    return google_oauth2.authorize(callback=callback)

@application.route("/authenticate/google")
@google_oauth2.authorized_handler
def authorized(resp):
    access_token = resp.get('access_token')

    headers = {'Authorization': 'OAuth '+access_token}
    response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
    if response.status_code != 200:
        logger.info({"response": response.content, "status_code": response.status_code})
        return render_template("login-failed.html")

    data = response.json()
    data["jwt"] = jwt_auth.jwt_encode_callback({"email": data["email"]})

    return redirect("{}?jwt={}".format(conf.REDIRECT_AFTER_LOGIN, data["jwt"]))

@google_oauth2.tokengetter
def get_access_token():
    return session.get('access_token')


@application.route("/v2/plugins")
def plugins():
    return make_response(json.dumps(get_plugin_registry_data()), 200)

@application.route("/v2/plugins/<string:plugin_id>/main.js")
def main_js(plugin_id):
    return redirect("static/plugins/{}/main.js".format(plugin_id))

