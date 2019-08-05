from asgard.models.base import BaseModel


class ScheduleSpec(BaseModel):
    value: str
    tz: str = "UTC"
