from pydantic import BaseModel
from typing import Optional


class DecisionDto(BaseModel):
    id: str
    mem: Optional[float]
    cpus: Optional[float]

    def dict(self, *args, **kwargs):
        decision_dict = {"id": self.id}

        if self.cpus:
            decision_dict["cpus"] = self.cpus

        if self.mem:
            decision_dict["mem"] = self.mem

        return decision_dict
