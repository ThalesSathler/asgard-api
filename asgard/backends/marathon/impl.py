from datetime import datetime, timezone
from decimal import Decimal

from aioelasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, A

from asgard.backends.base import AppsBackend, Interval
from asgard.conf import settings
from asgard.math import round_up
from asgard.models.account import Account
from asgard.models.app import App, AppStats
from asgard.models.user import User


class MarathonAppsBackend(AppsBackend):
    async def get_app_stats(
        self, app: App, interval: Interval, user: User, account: Account
    ) -> AppStats:
        utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
        index_name = f"asgard-app-stats-{utc_now.strftime('%Y-%m-%d')}-*"

        bool_query = Q(
            "bool",
            must=[
                Q("term", appname__keyword=f"/{account.namespace}/{app.id}"),
                Q("range", timestamp={"gte": f"now-{interval}"}),
            ],
        )
        query = Search().query(bool_query).extra(size=2)
        query.aggs.bucket("avg_cpu_pct", A("avg", field="cpu_pct"))
        query.aggs.bucket("avg_mem_pct", A("avg", field="mem_pct"))
        query.aggs.bucket("avg_cpu_thr_pct", A("avg", field="cpu_thr_pct"))
        dict_query = query.to_dict()

        errors = {}
        raw_result = None
        try:
            async with Elasticsearch([settings.STATS_API_URL]) as es:
                raw_result = await es.search(index=index_name, body=dict_query)
        except Exception as e:
            errors["global"] = str(e)

        if raw_result and raw_result["hits"]["hits"]:
            app_stats_result = raw_result["aggregations"]
            cpu_pct = round_up(
                Decimal(str(app_stats_result["avg_cpu_pct"]["value"]))
            )
            mem_pct = round_up(
                Decimal(str(app_stats_result["avg_mem_pct"]["value"]))
            )
            cpu_thr_pct = round_up(
                Decimal(str(app_stats_result["avg_cpu_thr_pct"]["value"]))
            )
        else:
            cpu_pct = Decimal(0)
            mem_pct = Decimal(0)
            cpu_thr_pct = Decimal(0)

        return AppStats(
            cpu_pct=str(cpu_pct),
            ram_pct=str(mem_pct),
            cpu_thr_pct=str(cpu_thr_pct),
            errors=errors,
        )
