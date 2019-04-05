import json
import os

os.environ["ENV"] = "TEST"

os.environ["TEST_DB_URL"] = os.getenv(
    "TEST_DB_URL", "postgresql://postgres@172.18.0.41/asgard"
)

MESOS_API_URLS = [
    "http://172.18.0.11:5050",
    "http://172.18.0.12:5050",
    "http://172.18.0.13:5050",
]

os.environ["TEST_MESOS_API_URLS"] = os.getenv(
    "TEST_MESOS_API_URLS", json.dumps(MESOS_API_URLS)
)
assert os.environ["ENV"] == "TEST"
