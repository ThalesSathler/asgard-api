from collections import defaultdict
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Union

from asgard.backends.mesos.models.app import MesosApp
from asgard.backends.mesos.models.task import MesosTask
from asgard.http.client import http_client
from asgard.math import round_up
from asgard.models.agent import Agent


class MesosAgent(Agent):
    type: str = "MESOS"
    id: str
    hostname: str
    active: bool
    version: str
    port: int
    used_resources: Dict[str, Union[str, int]]
    attributes: Dict[str, str]
    resources: Dict[str, Union[str, int]]
    total_apps: int = 0
    applications: List[MesosApp] = []
    stats: Optional[Dict[str, Any]] = {}

    # {
    #      "id": "4783cf15-4fb1-4c75-90fe-44eeec5258a7-S26",
    #      "hostname": "10.234.172.39",
    #      "port": 5051,
    #      "attributes": {
    #        "workload": "general",
    #        "owner": "asgard"
    #      },
    #      "pid": "slave(1)@10.234.172.39:5051",
    #      "registered_time": 1550665106.32753,
    #      "resources": {
    #        "disk": 44326,
    #        "mem": 2920,
    #        "gpus": 0,
    #        "cpus": 2,
    #        "ports": "[31000-32000]"
    #      },
    #      "used_resources": {
    #        "disk": 0,
    #        "mem": 1280,
    #        "gpus": 0,
    #        "cpus": 1,
    #        "ports": "[31471-31471, 31556-31556, 31634-31634, 31852-31852]"
    #      },
    #      "offered_resources": {
    #        "disk": 0,
    #        "mem": 0,
    #        "gpus": 0,
    #        "cpus": 0
    #      },
    #      "reserved_resources": {},
    #      "unreserved_resources": {
    #        "disk": 44326,
    #        "mem": 2920,
    #        "gpus": 0,
    #        "cpus": 2,
    #        "ports": "[31000-32000]"
    #      },
    #      "active": true,
    #      "version": "1.4.1",
    #      "capabilities": [
    #        "MULTI_ROLE",
    #        "HIERARCHICAL_ROLE",
    #        "RESERVATION_REFINEMENT"
    #      ],
    #      "reserved_resources_full": {},
    #      "unreserved_resources_full": [
    #        {
    #          "name": "cpus",
    #          "type": "SCALAR",
    #          "scalar": {
    #            "value": 2
    #          },
    #          "role": "*"
    #        },
    #        {
    #          "name": "mem",
    #          "type": "SCALAR",
    #          "scalar": {
    #            "value": 2920
    #          },
    #          "role": "*"
    #        },
    #        {
    #          "name": "disk",
    #          "type": "SCALAR",
    #          "scalar": {
    #            "value": 44326
    #          },
    #          "role": "*"
    #        },
    #        {
    #          "name": "ports",
    #          "type": "RANGES",
    #          "ranges": {
    #            "range": [
    #              {
    #                "begin": 31000,
    #                "end": 32000
    #              }
    #            ]
    #          },
    #          "role": "*"
    #        }
    #      ],
    #      "used_resources_full": [
    #        {
    #          "name": "cpus",
    #          "type": "SCALAR",
    #          "scalar": {
    #            "value": 1
    #          },
    #          "role": "*",
    #          "allocation_info": {
    #            "role": "*"
    #          }
    #        },
    #        {
    #          "name": "mem",
    #          "type": "SCALAR",
    #          "scalar": {
    #            "value": 1280
    #          },
    #          "role": "*",
    #          "allocation_info": {
    #            "role": "*"
    #          }
    #        },
    #        {
    #          "name": "ports",
    #          "type": "RANGES",
    #          "ranges": {
    #            "range": [
    #              {
    #                "begin": 31471,
    #                "end": 31471
    #              },
    #              {
    #                "begin": 31556,
    #                "end": 31556
    #              },
    #              {
    #                "begin": 31634,
    #                "end": 31634
    #              },
    #              {
    #                "begin": 31852,
    #                "end": 31852
    #              }
    #            ]
    #          },
    #          "role": "*",
    #          "allocation_info": {
    #            "role": "*"
    #          }
    #        }
    #      ],
    #      "offered_resources_full": []
    #    }

    def filter_by_attrs(self, kv):
        pass

    async def calculate_stats(self):
        """
        Calculate usage statistics.
            - CPU % usage
            - RAM % usage
        """
        cpu_pct = (
            Decimal(self.used_resources["cpus"])
            / Decimal(self.resources["cpus"])
            * 100
        )

        ram_pct = (
            Decimal(self.used_resources["mem"])
            / Decimal(self.resources["mem"])
            * 100
        )

        self.stats = {
            "cpu_pct": str(round_up(cpu_pct)),
            "ram_pct": str(round_up(ram_pct)),
        }

    async def apps(self) -> List[MesosApp]:
        self_address = f"http://{self.hostname}:{self.port}"
        containers_url = f"{self_address}/containers"
        apps = []
        async with http_client.get(containers_url) as response:
            data = await response.json()
            all_apps: Set[str] = set()
            for container_info in data:
                app_id = MesosApp.transform_to_asgard_app_id(
                    container_info["executor_id"]
                )
                if app_id not in all_apps:
                    apps.append(MesosApp(**{"id": app_id}))
                    all_apps.add(app_id)
            return apps

    async def tasks(self, app_id: str) -> List[MesosTask]:
        self_address = f"http://{self.hostname}:{self.port}"
        containers_url = f"{self_address}/containers"
        async with http_client.get(containers_url) as response:
            data = await response.json()
            tasks_per_app: Dict[str, List[MesosTask]] = defaultdict(list)
            for container_info in data:
                app_id_ = MesosApp.transform_to_asgard_app_id(
                    container_info["executor_id"]
                )
                tasks_per_app[app_id_].append(
                    MesosTask(
                        **{
                            "name": MesosTask.transform_to_asgard_task_id(
                                container_info["executor_id"]
                            )
                        }
                    )
                )
            return tasks_per_app[app_id]
