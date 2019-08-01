from typing import Dict, Optional

from pydantic import BaseModel

class ScalableApp(BaseModel):
    id: str
    cpu: float
    mem: float
    labels: Optional[Dict[str, str]]
