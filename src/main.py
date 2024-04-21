from pathlib import Path
import typer
from cli.distribute_inbox import distribute_inbox

cli_app = typer.Typer()


@cli_app.command(
    help='If no savePath is provided, the output will be saved to "output.txt"'
)
def parse(filepath: str, save_path: str = "output.txt") -> None:
    distribute_inbox(source_file=Path(filepath), dest_file=Path(save_path))


if __name__ == "__main__":
    cli_app()
