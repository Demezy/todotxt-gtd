from dataclasses import dataclass, replace
from datetime import datetime
from typing import Callable

from config import Priority
from pyrsistent import PMap, PSet, PVector
from returns.maybe import Maybe

TaskProject = str
TaskContext = str
TaskProperties = PMap[str, str]


@dataclass(frozen=True)
class TaskEntity:
    projects: PSet[TaskProject]
    contexts: PSet[TaskContext]
    text: str
    due_date: Maybe[datetime]
    priority: Maybe[Priority]
    is_done: bool
    properties: TaskProperties

    def update_done(self, is_done: bool) -> "TaskEntity":
        return replace(self, is_done=is_done)

    def add_project(self, project: TaskProject) -> "TaskEntity":
        return replace(self, projects=self.projects.add(project))

    def remove_project(self, project: TaskProject) -> "TaskEntity":
        return replace(self, projects=self.projects.remove(project))

    def add_context(self, context: TaskContext) -> "TaskEntity":
        return replace(self, contexts=self.contexts.add(context))

    def remove_context(self, context: TaskContext) -> "TaskEntity":
        return replace(self, contexts=self.contexts.remove(context))

    def update_text(self, text_transformer: Callable[[str], str]) -> "TaskEntity":
        return replace(self, text=text_transformer(self.text))

    def update_due_date(self, due_date: Maybe[datetime]) -> "TaskEntity":
        return replace(self, due_date=due_date)

    def update_priority(self, priority: Maybe[Priority]) -> "TaskEntity":
        return replace(self, priority=priority)


TaskList = PVector[TaskEntity]
TaskPredicate = Callable[[TaskEntity], bool]
