from asgard.models.base import BaseModel


class FetchURLSpec(BaseModel):
    uri: str
    extract: bool = True
    executable: bool = False
    cache: bool = False
