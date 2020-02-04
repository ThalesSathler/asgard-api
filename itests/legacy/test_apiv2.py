import json
from typing import Dict
from unittest.mock import patch

from flask import Response
from responses import RequestsMock

from asgard.models.account import Account
from asgard.models.user import UserDB
from hollowman import conf
from hollowman.app import application
from hollowman.auth.jwt import jwt_auth, jwt_generate_user_info
from itests.util import (
    BaseTestCase,
    ACCOUNT_DEV_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
    USER_WITH_MULTIPLE_ACCOUNTS_NAME,
)
from tests.utils import with_json_fixture


class AuthenticationTest(BaseTestCase):
    async def setUp(self):
        await super(AuthenticationTest, self).setUp()

        self.normal_user = UserDB(
            tx_email=USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
            tx_name=USER_WITH_MULTIPLE_ACCOUNTS_NAME,
        )
        self.account = Account(**ACCOUNT_DEV_DICT)

        self.response_http_200 = Response(status=200)

    async def tearDown(self):
        await super(AuthenticationTest, self).tearDown()
        patch.stopall()

    def make_auth_header(self, user, account) -> Dict[str, str]:
        jwt_token = jwt_auth.jwt_encode_callback(
            jwt_generate_user_info(user, account)
        )
        return {"Authorization": "JWT {}".format(jwt_token.decode("utf-8"))}

    @with_json_fixture("single_full_app.json")
    def test_it_creates_a_response_using_a_dict_of_headers(self, fixture):
        """
        O atributo headers de um objeto `request.models.Response` é utilizado
        para gerar o response do hollowman. Por ser do tipo `CaseInsentiveDict`,
        quebra a implementação do flask e faz com que seja necessário o typecast
        para `dict`.
        """
        test_client = application.test_client()
        with application.app_context():
            auth_header = self.make_auth_header(self.normal_user, self.account)
            with RequestsMock() as rsps:
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0] + "/v2/apps",
                    body=json.dumps({"apps": [fixture]}),
                    status=200,
                )
                rsps.add(
                    method="GET",
                    url=conf.MARATHON_ADDRESSES[0]
                    + f"/v2/groups//{self.account.namespace}/",
                    body=json.dumps({"apps": [fixture]}),
                    status=200,
                )
                r = test_client.get("/v2/apps", headers=auth_header)
                self.assertEqual(200, r.status_code)
