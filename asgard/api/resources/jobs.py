from typing import Optional, List

from pydantic import BaseModel

from asgard.models.job import ScheduledJob


class ScheduledJobResource(BaseModel):
    job: Optional[ScheduledJob]


class ScheduledJobsListResource(BaseModel):
    jobs: Optional[List[ScheduledJob]]
