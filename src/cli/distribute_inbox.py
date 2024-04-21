from pathlib import Path

from flupy import flu
from returns.io import IO

from app_failure import IOResultAF
from impure.filesystem import create_file, write_file_lines
from impure.io import ioprint
from impure.user_io import (
    prompt_context,
    promt_until_valid,
)
from tasks.show_task import show_task
from tasks.task_entity import TaskContext, TaskEntity
from todotxt.parser import (
    todotxt_from_task,
)
from todotxt.from_file import tasks_from_todo_txt_file
from utils import (
    flatten_result_io,
    result_io_flatmap,
)


def _is_task_with_context(task: TaskEntity) -> bool:
    return len(task.contexts) != 0


def _prompt_context_until_valid() -> IO[TaskContext]:
    return promt_until_valid(
        prompt_context,
        "Choose predefined context or set up it in config",
    )


def _task_with_context_prompt(task: TaskEntity) -> IO[TaskEntity]:
    if _is_task_with_context(task):
        return IO(task)

    return IO.do(
        task.add_context(context)
        for _ in ioprint(show_task(task))
        for context in _prompt_context_until_valid()
    )


def distribute_inbox(source_file: Path, dest_file: Path) -> None:
    tasks = tasks_from_todo_txt_file(source_file)

    distributed_tasks = result_io_flatmap(tasks, _task_with_context_prompt)

    # no error during read write
    assert distributed_tasks.value_or(False)
    # all tasks processed
    assert tasks.map(len) == distributed_tasks.map(len)
    # all tasks have context
    assert distributed_tasks.map(
        lambda x: all(flu(x).map(_is_task_with_context))
    ).value_or(False) == IO(True)

    created = create_file(dest_file, overwrite=True)
    # add error handling instead
    assert created.value_or(False)

    saved: IOResultAF[None] = flatten_result_io(
        distributed_tasks.unwrap()
        .map(lambda tasks: flu(tasks).map(todotxt_from_task).to_list())
        .map(lambda x: write_file_lines(dest_file, x))
    )
    assert saved.map(lambda _: True).value_or(False)
