from rich.prompt import Prompt


def parse_inbox(data: list[str], bins: dict[str, str]) -> list[str]:
    """
    Iterates through the todos and prompts the user to move the todo to a bin.
    """

    index = 0
    while index < len(data):
        todo = data[index]

        # skip if todo is already in a bin
        if any(bin in todo for bin in bins.values()):
            index += 1
            continue

        # prompt which state to move the todo to
        state = Prompt.ask(
            f"\n[bold cyan]todo[/bold cyan]:\n\t{todo}\n[yellow]enter first letter[/yellow]\n"
            + f"{'\n'.join([f'({k}) {v.replace('_', '')}' for k, v in bins.items()])}\n"
        )
        if state in bins:
            data[index] = f"{todo} @{bins[state]}"
            print(f"[yellow]saved as[/yellow]: {data[index]}\n")
            index += 1

    return data
