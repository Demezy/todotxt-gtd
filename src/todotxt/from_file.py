from app_failure import AppFailure
from impure.filesystem import file_lines
from impure.user_io import user_fixed_tasks
from tasks.task_entity import TaskEntity
from todotxt.parser import task_from_todotxt_or_same
from utils import flatten_io_result


from pyrsistent import pvector
from pyrsistent.typing import PVector
from returns.io import IOResult


from pathlib import Path


def tasks_from_todo_txt_file(
    source_file: Path,
) -> IOResult[PVector[TaskEntity], AppFailure]:
    return flatten_io_result(
        file_lines(source_file)
        # parse strings
        .map(
            lambda strings: pvector(
                task_from_todotxt_or_same(x) for x in strings if x != ""
            )
        )
        # recover if needed
        .map(user_fixed_tasks)
    )
