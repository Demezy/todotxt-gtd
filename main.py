import typer
from rich import print
from config import BINS
from src.cli_app import parse_inbox

cli_app = typer.Typer()


@cli_app.command(
    help='If no savePath is provided, the output will be saved to "output.txt"'
)
def parse(filepath: str, savePath: str = "output.txt"):
    data = []
    with open(filepath, "r") as f:
        data = [line.strip() for line in f.readlines()]

    parse_inbox(data, BINS)

    print(f"writing to {savePath}")

    with open(savePath, "w") as f:
        f.write("\n".join(data) + "\n")

    print("done")


if __name__ == "__main__":
    cli_app()
