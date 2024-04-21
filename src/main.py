import dis
from pathlib import Path

from flupy import flu

from app_failure import AppFailure, IOResultAF
from impure.filesystem import create_file, file_lines, write_file_lines
from impure.io import iopprint, ioprint
from impure.user_io import (
    prompt_context,
    promt_until_valid,
    user_fixed_tasks,
)
from pyrsistent import pvector
from returns.io import IO, IOResult
from returns.converters import flatten
from returns.functions import tap, identity
from tasks.show_task import show_task
from tasks.task_entity import TaskContext, TaskEntity
from todotxt.parser import (
    task_from_todotxt_or_same,
    todotxt_from_task,
)

from utils import (
    flatten_result_io,
    result_io_flatmap,
    flatten_io_result,
)

TESTTXT = Path("test.txt")
MORETEST = Path("tasks.todotxt")
SAVEPATH = Path("output.todotxt")


tasks = flatten_io_result(
    file_lines(Path(MORETEST))
    # parse strings
    .map(lambda strings: pvector(task_from_todotxt_or_same(x) for x in strings))
    # recover if needed
    .map(user_fixed_tasks)
)


def is_task_with_context(task: TaskEntity) -> bool:
    return len(task.contexts) != 0


def prompt_context_until_valid() -> IO[TaskContext]:
    return promt_until_valid(
        prompt_context,
        "Choose predefined context or set up it in config",
    )


def task_with_context_prompt(task: TaskEntity) -> IO[TaskEntity]:
    if is_task_with_context(task):
        return IO(task)

    return IO.do(
        task.add_context(context)
        for _ in ioprint(show_task(task))
        for context in prompt_context_until_valid()
    )


distributed_tasks = result_io_flatmap(tasks, task_with_context_prompt)

# no error during read write
assert distributed_tasks.value_or(False)
# all tasks processed
assert tasks.map(len) == distributed_tasks.map(len)
# all tasks have context
assert distributed_tasks.map(lambda x: all(flu(x).map(is_task_with_context))).value_or(
    False
) == IO(True)


created = create_file(SAVEPATH, overwrite=True)
assert created.value_or(False)

saved: IOResultAF[None] = flatten_result_io(
    distributed_tasks.unwrap()
    .map(lambda tasks: flu(tasks).map(todotxt_from_task).to_list())
    .map(lambda x: write_file_lines(SAVEPATH, x))
)

print(saved)
