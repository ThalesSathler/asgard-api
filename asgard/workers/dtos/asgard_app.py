from typing import Dict, Optional

from pydantic import BaseModel


class App(BaseModel):
    id: str
    cpu: float
    mem: float
    labels: Optional[Dict[str, str]]


class StatsSpec(BaseModel):
    type: str
    cpu_pct: str
    ram_pct: str
    cpu_thr_pct: str


class AppStats(BaseModel):
    id: str
    stats: StatsSpec
