import json
import os

ENV = "TEST"
os.environ["ENV"] = ENV

VALUES = {
    # Envs para códigos externos
    # Envs para a asgard API
    "DB_URL": "postgresql://postgres@172.18.0.41/asgard",
    "STATS_API_URL": "http://172.18.70.1:9200",
    "MESOS_API_URLS": json.dumps(
        [
            "http://172.18.0.11:5050",
            "http://172.18.0.12:5050",
            "http://172.18.0.13:5050",
        ]
    ),
    "SCHEDULED_JOBS_SERVICE_ADDRESS": "http://172.18.0.40:9090",
    "SCHEDULED_JOBS_SERVICE_AUTH": json.dumps(
        {"user": "chronos", "password": "secret"}
    ),
    "AUTOSCALER_AUTH_TOKEN": "anytoken",
    "AUTOSCALER_MARGIN_THRESHOLD": "0.05",
    "SCHEDULED_JOBS_DEFAULT_FETCH_URIS": json.dumps(
        [
            {"uri": "file:///etc/docker.tar.bz2"},
            {"uri": "file:///etc/config.bz2"},
        ]
    ),
}


for name, value in VALUES.items():
    os.environ[f"{ENV}_{name}"] = os.getenv(f"{ENV}_{name}", value)

os.environ["TEST_ASGARD_API_ADDRESS"] = os.getenv(
    "TEST_ASGARD_API_ADDRESS", "http://localhost:5000"
)

assert os.environ["ENV"] == "TEST"
