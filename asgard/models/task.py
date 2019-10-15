import abc

from .base import BaseModel


class Task(BaseModel, abc.ABC):
    @abc.abstractclassmethod
    def transform_to_asgard_task_id(cls, executor_id: str) -> str:
        raise NotImplementedError
