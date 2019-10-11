from asgard.models.task import Task


class MesosTask(Task):
    type: str = "MESOS"

    name: str

    @classmethod
    def transform_to_asgard_task_id(cls, executor_id: str) -> str:
        task_name_part = executor_id.split("_")[1:]
        return "_".join(task_name_part)
