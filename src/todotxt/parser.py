import re
from datetime import datetime

from config import Priority
from pyrsistent import PSet, freeze
from returns.converters import maybe_to_result
from returns.maybe import Maybe, Some, maybe, Nothing
from returns.result import Result, Success, Failure
from tasks.task_entity import TaskEntity, TaskProject, TaskProperties
from utils import maybe_get_enum, maybe_get_map

TodoStr = str


def _priority_from_todotxt(todo: TodoStr) -> Maybe[Priority]:
    return Maybe.do(
        priority
        for match_group in maybe(re.search)(r"\(([A-Z])\)", todo)
        for match in Maybe.from_optional(match_group.group(1))
        for priority in maybe_get_enum(Priority, match)
    )


def _projects_from_todotxt(todo: TodoStr) -> PSet[TaskProject]:
    projects_strings = {match for match in re.findall(r" \+(\w+)", todo)}

    return freeze(projects_strings)


def _contexts_from_todotxt(todo: TodoStr) -> PSet[TaskProject]:
    contexts_strings = {match for match in re.findall(r" @(\w+)", todo)}

    return freeze(contexts_strings)


def _due_date_from_properties(properties: TaskProperties) -> Maybe[datetime]:
    return Maybe.do(
        (
            datetime.strptime(date_string, "%Y-%m-%d")
            for date_string in maybe_get_map(properties, "due")
        ),
    )


def _is_done_from_todotxt(todo: TodoStr) -> bool:
    return bool(re.match(r"x ", todo))


def _properties_from_todotxt(todo: TodoStr) -> TaskProperties:
    return freeze(
        {
            match.group(1): match.group(2)
            for match in re.finditer(r" ([\w_-]+):([\w_-]+)", todo)
        }
    )


def _text_from_todotxt(todo: TodoStr) -> str:
    done_status_priority_removed = re.sub(r"^(x )?(\(([A-Z])\))?", "", todo)
    return re.sub(
        r"[\w_-]+:[\w_-]+| \+(\w+)| @(\w+)", "", done_status_priority_removed
    ).strip()


# it is impossible to create invalid syntax for todotxt actually. But if format would change, no guarantee
def task_from_todotxt(todo: TodoStr) -> Maybe[TaskEntity]:
    """
    Parses a todo string into a TaskEntity.
    """
    properties = _properties_from_todotxt(todo)

    return Some(
        TaskEntity(
            projects=_projects_from_todotxt(todo),
            contexts=_contexts_from_todotxt(todo),
            text=_text_from_todotxt(todo),
            due_date=_due_date_from_properties(properties),
            priority=_priority_from_todotxt(todo),
            is_done=_is_done_from_todotxt(todo),
            properties=_properties_from_todotxt(todo).discard("due"),
        )
    )


def todotxt_from_task(task: TaskEntity) -> str:
    is_done = "x" if task.is_done else ""
    priority = task.priority.map(lambda p: f"({p.value})").value_or("")
    projects = " ".join(f"+{project}" for project in task.projects)
    contexts = " ".join(f"@{context}" for context in task.contexts)
    properties = " ".join(f"{key}:{value}" for key, value in task.properties.items())
    due_date = task.due_date.map(lambda d: "due:" + d.strftime("%Y-%m-%d")).value_or("")

    return re.sub(
        r" +",
        " ",
        f"{is_done} {priority} {due_date} {task.text} {projects} {contexts} {properties}",
    ).strip()


TaskEntityOrStr = Result[TaskEntity, TodoStr]


def task_from_todotxt_or_same(todo: TodoStr) -> TaskEntityOrStr:
    """
    Try to parse a todo string into a TaskEntity. If it fails, it returns the original string in Failure.
    """
    return maybe_to_result(task_from_todotxt(todo)).alt(lambda _: todo)
