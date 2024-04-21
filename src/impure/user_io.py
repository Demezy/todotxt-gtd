from enum import Enum
from typing import Callable, Type, TypeVar, Union

from config import CONTEXTS, PROJECTS, Priority
from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.trampolines import Trampoline, trampoline
from returns.unsafe import unsafe_perform_io
from tasks.task_entity import TaskContext, TaskEntity, TaskProject
from impure.io import iopprint, ioprint, ioinput
from pyrsistent import PMap, PVector

from todotxt.parser import TaskEntityOrStr, TodoStr, task_from_todotxt
from utils import (
    io_vector,
    maybe_get_enum,
    maybe_get_map,
    result_recovered,
)


T = TypeVar("T")
E = TypeVar("E", bound=Enum)


def prompt_enum(title: str, enum: Type[E]) -> IO[Maybe[E]]:
    """
    Prompt the user to choose an enum value from a enum class.
    """
    return IO.do(
        maybe_get_enum(enum=enum, key=choose)
        for _ in ioprint(f"[yellow]{title}[/yellow]")
        for _ in ioprint(*enum._member_names_)
        for choose in ioinput()
    )


def prompt_map(title: str, options: PMap[str, T]) -> IO[Maybe[T]]:
    """
    Prompt the user to choose a value from a map.
    """

    return IO.do(
        maybe_get_map(map=options, key=choose)
        for _ in ioprint(f"[yellow]{title}[/yellow]")
        for _ in iopprint(options)
        for choose in ioinput()
    )


def prompt_project() -> IO[Maybe[TaskProject]]:
    """
    Prompt the user to choose a project.
    """
    return prompt_map("Choose a project: ", PROJECTS)


def prompt_context() -> IO[Maybe[TaskContext]]:
    """
    Prompt the user to choose a context.
    """
    return prompt_map("Choose a context: ", CONTEXTS)


def prompt_priority() -> IO[Maybe[Priority]]:
    """
    Prompt the user to choose a priority.
    """
    return prompt_enum("Choose a priority: ", Priority)


def maybe_fixed_from_str(parse_failed_task: TodoStr) -> IO[Maybe[TaskEntity]]:
    return IO.do(
        task_from_todotxt(new_todo)
        for new_todo in ioinput()
        for _ in ioprint(
            "\n[red]Failed to parse this todo:[/red]\n" + parse_failed_task
        )
        for _ in ioprint("[red]Please, manually fix syntax[/red]")
    )


def fixed_task_from_str(
    parse_failed_task: TodoStr,
) -> IO[TaskEntity]:
    return promt_until_valid(
        lambda: maybe_fixed_from_str(parse_failed_task=parse_failed_task)
    )


def user_fixed_tasks(
    tasks: PVector[TaskEntityOrStr],
) -> IO[PVector[TaskEntity]]:
    return io_vector(
        result_recovered(fixed_task_from_str, IOResult.from_result(task_r))
        for task_r in tasks
    )


@trampoline
def promt_until_valid(
    function: Callable[[], IO[Maybe[T]]],
    # it make no sense to repromt for pure function because of referential transparency
    message: str | None = None,
    # display message when the function return None
) -> Union[Trampoline[IO[T]], IO[T]]:
    """
    Re-run function until it return a value.
    Optionally print `message` if the function return None.
    """
    result = unsafe_perform_io(
        function()
    )  # used with caution, need to be wrapped in Trampoline

    # print message if function return Nothing
    result.or_else_call(lambda: iopprint(message) if message else None)

    # actually equivalent to while loop, but what an elegant way to write it
    return result.map(lambda value: IO(value)).value_or(
        Trampoline(promt_until_valid, function, message),
    )
