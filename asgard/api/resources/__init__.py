from typing import List

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    msg: str


class ErrorResource(BaseModel):
    errors: List[ErrorDetail]
