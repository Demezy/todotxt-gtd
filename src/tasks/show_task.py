from tasks.task_entity import TaskEntity


def show_task(task: TaskEntity) -> str:
    """
    Format the task as a string for display
    """
    heading = "[yellow]Task[/yellow]:"
    priority = task.priority.map(lambda p: f"[red]{p.value}[/red]").value_or(" ")
    due_date = task.due_date.map(
        lambda d: f"[blue]{d.strftime('%Y-%m-%d')}[/blue]"
    ).value_or("")
    text = task.text
    contexts = "[bright_green]" + ", ".join(task.contexts) + "[/bright_green]"
    projects = "[dark_green italic]" + ", ".join(task.projects) + "[/dark_green italic]"
    is_done = "[green]✔[/green]" if task.is_done else " "
    properties = (
        "[magenta italic]"
        + ", ".join([f"{k}: {v}" for k, v in task.properties.items()])
        + "[/magenta italic]"
    )

    return " ".join(
        [
            heading,
            is_done,
            priority,
            due_date,
            text,
            contexts,
            projects,
            properties,
        ]
    )
