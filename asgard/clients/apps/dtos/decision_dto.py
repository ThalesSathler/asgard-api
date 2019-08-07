class DecisionDto:
    id: str
    mem: int
    cpus: float

    def to_dict(self):
        decision_dict = {
            "id": self.id
        }

        if self.cpus:
            decision_dict["cpus"] = self.cpus

        if self.mem:
            decision_dict["mem"] = self.mem

        return decision_dict

