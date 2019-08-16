from asgard.backends.base import Orchestrator, Interval
from asgard.backends.mesos.models.app import MesosApp
from asgard.models.account import Account
from asgard.models.app import AppStats
from asgard.models.user import User


class AppsService:
    @staticmethod
    async def get_app_stats(
        app_id: str,
        interval: Interval,
        user: User,
        account: Account,
        orchestrator: Orchestrator,
    ) -> AppStats:
        """
        Retorna estatísticas de uso de CPU/RAM/CPU thr de uma app. O Cálculo considera todas as instâncias dessa app.
        Retorna um objeto :py:class:`AppStats <asgard.models.app.AppStats>`
        """
        app = MesosApp(id=app_id)
        return await orchestrator.get_app_stats(app, interval, user, account)
