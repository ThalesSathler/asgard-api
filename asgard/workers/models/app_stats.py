from pydantic import BaseModel

class StatsSpec(BaseModel):
    type: str
    cpu_pct: str
    ram_pct: str
    cpu_thr_pct: str

class AppStats(BaseModel):
    id: str
    stats: StatsSpec