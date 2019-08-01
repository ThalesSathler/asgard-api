import json
import os

ENV = "TEST"
os.environ["ENV"] = ENV

VALUES = {
    # Envs para códigos externos
    "ASYNCWORKER_HTTP_PORT": "9999",
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
}


for name, value in VALUES.items():
    os.environ[f"{ENV}_{name}"] = os.getenv(f"{ENV}_{name}", value)

assert os.environ["ENV"] == "TEST"
