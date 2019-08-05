from asgard.api.resources.users import UserMeResource
from asgard.db import AsgardDBSession
from asgard.models.account import AccountDB, Account
from asgard.models.user import UserDB, User
from itests.util import (
    BaseTestCase,
    ACCOUNT_DEV_ID,
    ACCOUNT_DEV_NAME,
    ACCOUNT_DEV_NAMESPACE,
    ACCOUNT_DEV_OWNER,
    ACCOUNT_INFRA_ID,
    ACCOUNT_INFRA_NAME,
    ACCOUNT_INFRA_NAMESPACE,
    ACCOUNT_INFRA_OWNER,
    USER_WITH_MULTIPLE_ACCOUNTS_ID,
    USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
    USER_WITH_MULTIPLE_ACCOUNTS_NAME,
)


class UsersMeResourcesTest(BaseTestCase):
    async def setUp(self):
        await super(UsersMeResourcesTest, self).setUp()

    async def tearDown(self):
        await super(UsersMeResourcesTest, self).tearDown()

    async def test_serialize_all_fields(self):
        """
        Confere que é possível serializar um UsersMeResources a apartir dos
        outros modelos necessários.
        data = UsersMeResources(user=..., current_account=..., accounts=...)
        """
        async with AsgardDBSession() as s:
            account = (
                await s.query(AccountDB)
                .filter(AccountDB.id == ACCOUNT_DEV_ID)
                .one()
            )
            other_accounts = (
                await s.query(AccountDB)
                .filter(AccountDB.id == ACCOUNT_INFRA_ID)
                .one()
            )
            user = (
                await s.query(UserDB)
                .filter(UserDB.id == USER_WITH_MULTIPLE_ACCOUNTS_ID)
                .one()
            )

            users_me_resource = UserMeResource(
                user=await User.from_alchemy_obj(user),
                current_account=await Account.from_alchemy_obj(account),
                accounts=[await Account.from_alchemy_obj(other_accounts)],
            )

            self.assertDictEqual(
                {
                    "accounts": [
                        {
                            "id": ACCOUNT_INFRA_ID,
                            "name": ACCOUNT_INFRA_NAME,
                            "namespace": ACCOUNT_INFRA_NAMESPACE,
                            "owner": ACCOUNT_INFRA_OWNER,
                            "type": "ASGARD",
                        }
                    ],
                    "current_account": {
                        "id": ACCOUNT_DEV_ID,
                        "name": ACCOUNT_DEV_NAME,
                        "namespace": ACCOUNT_DEV_NAMESPACE,
                        "owner": ACCOUNT_DEV_OWNER,
                        "type": "ASGARD",
                    },
                    "user": {
                        "email": USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
                        "id": USER_WITH_MULTIPLE_ACCOUNTS_ID,
                        "name": USER_WITH_MULTIPLE_ACCOUNTS_NAME,
                        "type": "ASGARD",
                    },
                },
                users_me_resource.dict(),
            )
