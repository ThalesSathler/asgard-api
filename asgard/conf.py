import os
from typing import List, Optional

from pydantic import BaseSettings, BaseModel

from asgard.models.spec.fetch import FetchURLSpec

ASGARD_RABBITMQ_HOST = "127.0.0.1"
ASGARD_RABBITMQ_USER = "guest"
ASGARD_RABBITMQ_PASS = "guest"
ASGARD_RABBITMQ_PREFETCH = 32

ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT = int(
    os.getenv("ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT", 1)
)
ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT = int(
    os.getenv("ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT", 30)
)

# Configs que foram migradas do pacote `hollowman.conf`.
# Depois vamos mudar o prefixo de `HOLLOWMAN_` para `ASGARD_`
SECRET_KEY = os.getenv("HOLLOWMAN_SECRET_KEY", "secret")
TASK_FILEREAD_MAX_OFFSET: int = int(
    os.getenv("ASGARD_TASK_FILEREAD_MAX_OFFSET", 52_428_800)
)


class AuthSpec(BaseModel):
    user: Optional[str]
    password: Optional[str]


class Settings(BaseSettings):

    MESOS_API_URLS: List[str]
    DB_URL: str
    STATS_API_URL: str
    SCHEDULED_JOBS_SERVICE_ADDRESS: str
    SCHEDULED_JOBS_SERVICE_AUTH: AuthSpec = AuthSpec()
    SCHEDULED_JOBS_DEFAULT_FETCH_URIS: List[FetchURLSpec] = []

    class Config:
        env_prefix = os.getenv("ENV", "ASGARD") + "_"


settings = Settings()
