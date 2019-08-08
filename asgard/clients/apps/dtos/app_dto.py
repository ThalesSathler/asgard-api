from typing import Optional, Dict

from pydantic import BaseModel


class AppDto(BaseModel):
    id: str
    cpu: float
    mem: float
    labels: Optional[Dict[str, str]]
