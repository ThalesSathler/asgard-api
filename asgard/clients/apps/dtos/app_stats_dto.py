from pydantic import BaseModel


class StatsSpec(BaseModel):
    type: str
    cpu_pct: str
    ram_pct: str
    cpu_thr_pct: str


class AppStatsDto(BaseModel):
    id: str
    stats: StatsSpec

    def was_not_found(self) -> bool:
        return self.stats.cpu_pct == "0" and self.stats.ram_pct == "0" and self.stats.cpu_thr_pct == "0"
