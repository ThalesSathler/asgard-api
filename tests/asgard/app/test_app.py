from importlib import reload

import asynctest
from asyncworker import RouteTypes

from asgard import app, conf


class AsgardAppTest(asynctest.TestCase):
    async def test_load_with_conf_values(self):
        with asynctest.mock.patch.multiple(
            conf,
            ASGARD_RABBITMQ_HOST="10.0.0.1",
            ASGARD_RABBITMQ_USER="user1",
            ASGARD_RABBITMQ_PASS="pass1",
            ASGARD_RABBITMQ_PREFETCH=64,
        ):
            reload(app)
            conn = app.app.connections.with_type(RouteTypes.AMQP_RABBITMQ)
            self.assertEqual(1, len(conn))
            self.assertEqual("10.0.0.1", conn[0].hostname)
            self.assertEqual("user1", conn[0].username)
            self.assertEqual("pass1", conn[0].password)
            self.assertEqual(64, conn[0].prefetch)
