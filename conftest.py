import json
import os

os.environ["ENV"] = "TEST"

os.environ["TEST_DB_URL"] = os.getenv(
    "TEST_DB_URL", "postgresql://postgres@172.18.0.41/asgard"
)

os.environ["TEST_STATS_API_URL"] = os.getenv(
    "TEST_STATS_API_URL", "http://172.18.70.1:9200"
)

os.environ["TEST_ASYNCWORKER_HTTP_PORT"] = os.getenv(
    "TEST_ASYNCWORKER_HTTP_PORT", "9999"
)

MESOS_API_URLS = [
    "http://172.18.0.11:5050",
    "http://172.18.0.12:5050",
    "http://172.18.0.13:5050",
]

os.environ["TEST_MESOS_API_URLS"] = os.getenv(
    "TEST_MESOS_API_URLS", json.dumps(MESOS_API_URLS)
)

os.environ["TEST_ASGARD_API_ADDRESS"] = os.getenv(
    "TEST_ASGARD_API_ADDRESS", "http://localhost:5000"
)

assert os.environ["ENV"] == "TEST"
