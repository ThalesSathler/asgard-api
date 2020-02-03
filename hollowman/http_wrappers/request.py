import json
from typing import Dict, Iterable

from marathon import MarathonApp, NotFoundError
from marathon.models.group import MarathonGroup
from marathon.models.task import MarathonTask
from marathon.util import MarathonMinimalJsonEncoder

from hollowman.hollowman_flask import HollowmanRequest
from hollowman.http_wrappers.base import Apps, HTTPWrapper
from hollowman.marathon.group import AsgardAppGroup
from hollowman.marathonapp import AsgardApp

# Keys que são multi-valor e que devem
# ser mergeados de forma especial quando
# juntamos a request_app com a original_app
REMOVABLE_KEYS = {
    "constraints",
    "labels",
    "env",
    "healthChecks",
    "upgradeStrategy",
}


class Request(HTTPWrapper):
    json_encoder = MarathonMinimalJsonEncoder

    app_path_prefix = "/v2/apps"
    group_path_prefix = "/v2/groups"

    def __init__(self, request: HollowmanRequest):
        self.request = request

    def merge_marathon_apps(self, modified_app, base_app):
        """
        A junção das duas apps (request_app (aqui modified_app) e original_app (aqui base_app)) é
        sempre feita pegando todos os dados da original_app e jogando os dados da requst_app "em cima".
        Não podemos usar o `minimal=Fase` na request_app pois para requests que estão *incompletos*, ou seja,
        sem alguns vampos (já veremos exemplo) se usássemos minimal=False, iríramos apagar esses "campos faltantes"
        da original_app. Exemplos:

            request_app = {"instances": 10}
            original_app está completa, com envs, constraints e tudo mais.

            se usamos `minimal=False` na request_app, teremos um JSON com *todos* os campos em branco, menos o "instances".
            Então quando fizermos `merged.update(modified_app.json_repr(minimal=False))`, vamos no final ter um JSON apenas com
            o campo "instances" perrnchido e todo o restante vazio.


        """

        merged = base_app.json_repr(minimal=False)
        merged.update(modified_app.json_repr(minimal=True))
        try:
            raw_request_data = json.loads(self.request.data)
            for key in REMOVABLE_KEYS:
                if key in raw_request_data:
                    merged[key] = raw_request_data[key]
        except Exception as e:
            pass
        if isinstance(base_app, MarathonTask):
            return MarathonTask.from_json(merged)
        return AsgardApp.from_json(merged)

    def get_request_data(self) -> Iterable[Dict]:
        if not self.request.data:
            return [{}]

        data = self.request.get_json()
        """
        Matrathon's UI POST request to '/v2/apps/*/restart' contains a body
        with `{"force": (true|false)}` which isn't compatible with `MarathonApp`
        interface and marathons api, and should be removed.
        """
        if not isinstance(data, list):
            data.pop("force", None)
            return [data]
        return data

    def split(self) -> Apps:

        if self.is_read_request():
            if self.is_list_apps_request():
                apps = list(
                    self._get_original_group(
                        self.request.user, self.object_id
                    ).iterate_apps()
                )
                for app in apps:
                    yield self.merge_marathon_apps(MarathonApp(), app), app
            elif self.is_app_request():
                app = self._get_original_app(self.request.user, self.object_id)
                yield self.merge_marathon_apps(MarathonApp(), app), app
            elif self.is_group_request():
                self.group = self._get_original_group(
                    self.request.user, self.object_id
                )
                for app in self.group.iterate_apps():
                    yield self.merge_marathon_apps(MarathonApp(), app), app

            return

        # Request is a WRITE
        if self.is_app_request():
            for app in self.get_request_data():
                request_app = MarathonApp.from_json(app)
                app = self._get_original_app(
                    self.request.user, self.object_id or request_app.id
                )

                yield self.merge_marathon_apps(request_app, app), app
        elif self.is_tasks_request():
            request_data = self.request.get_json()
            for task_id in request_data["ids"]:
                request_task = MarathonTask.from_json({"id": task_id})
                yield request_task, request_task
            return

    def _rindex(self, iterable, value):
        """
        Busca o valor de `value` dentro do iterável `iterable`, mas começando do final.
        https://stackoverflow.com/questions/522372/finding-first-and-last-index-of-some-value-in-a-list-in-python
        """
        return len(iterable) - iterable[::-1].index(value) - 1

    def _adjust_request_path_if_needed(self, request, modified_app_or_group):
        original_path = request.path.rstrip("/")
        original_path_parts = original_path.split("/")
        if original_path.startswith("/v2/apps") and original_path != "/v2/apps":
            app_id = modified_app_or_group.id or self.object_id
            last_app_id_part = app_id.split("/")[-1]
            last_part_position = self._rindex(
                original_path_parts, last_app_id_part
            )
            extra = original_path_parts[last_part_position + 1 :]
            request.path = "/v2/apps{app_id}/{extra}".format(
                app_id=app_id.rstrip("/"), extra="/".join(extra)
            )
            request.path = request.path.rstrip("/")
        if original_path.startswith("/v2/groups"):
            extra = []
            group_id = modified_app_or_group.id or self.group_id
            group_id = group_id.rstrip("/")
            last_app_id_part = group_id.split("/")[-1]
            if last_app_id_part in original_path_parts:
                last_part_position = self._rindex(
                    original_path_parts, last_app_id_part
                )
                extra = original_path_parts[last_part_position + 1 :]
            request.path = "/v2/groups{group_id}/{extra}".format(
                group_id=group_id.rstrip("/"), extra="/".join(extra)
            )
            request.path = request.path.rstrip("/")

    def join(self, apps: Apps) -> HollowmanRequest:
        request = HollowmanRequest(environ=self.request.environ, shallow=True)

        if self.is_read_request() and self.is_app_request():
            """
            OperationType.READ derived request filters are
            readonly and dont manipulate the request
            """
            if not apps:
                request.data = json.dumps([])
                return self.request
            request_app, original_app = apps[0]
            self._adjust_request_path_if_needed(self.request, original_app)
            return self.request

        if self.is_read_request() and self.is_group_request():
            self._adjust_request_path_if_needed(self.request, self.group)
            return self.request

        if self.is_read_request() and self.is_queue_request():
            return self.request

        if self.is_list_apps_request():
            apps_json_repr = [
                request_app.json_repr(minimal=True) for request_app, _ in apps
            ]
            if self.is_post():
                # Post em /v2/apps nao poder ser uma lista, tem que ser apenas uma app.
                apps_json_repr = apps_json_repr[0]
        elif self.is_delete():
            if self.is_group_request():
                group_id = self.object_id
                group_id_with_namespace = "/{}/{}".format(
                    self.request.user.current_account.namespace,
                    group_id.strip("/"),
                )
                self.request.path = "/v2/groups{}".format(
                    group_id_with_namespace
                )
            if self.is_app_request():
                group_id = self.object_id
                group_id_with_namespace = "/{}/{}".format(
                    self.request.user.current_account.namespace,
                    group_id.strip("/"),
                )
                self.request.path = "/v2/apps{}".format(group_id_with_namespace)
            if self.is_queue_request():
                app_id = self.object_id
                app_id_with_namespace = "/{}/{}".format(
                    self.request.user.current_account.namespace,
                    app_id.strip("/"),
                )
                self.request.path = "/v2/queue{}/delay".format(
                    app_id_with_namespace
                )

            return self.request
        elif self.is_tasks_request():
            if self.is_read_request():
                return self.request
            if self.is_write_request():
                apps_json_repr = {"ids": []}
                for request_task, _ in apps:
                    apps_json_repr["ids"].append(request_task.id)

        else:
            request_app, original_app = apps[0]
            self._adjust_request_path_if_needed(request, original_app)
            apps_json_repr = request_app.json_repr(minimal=False)

        request.data = json.dumps(apps_json_repr, cls=self.json_encoder)
        return request
