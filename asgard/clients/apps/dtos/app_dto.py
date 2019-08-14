from typing import Optional, Dict

from pydantic import BaseModel


class AppDto(BaseModel):
    id: str
    cpus: float
    mem: float
    labels: Optional[Dict[str, str]]
