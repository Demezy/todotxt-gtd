from pathlib import Path

from app_failure import AppFailure, IOResultAF
from pyrsistent import freeze
from pyrsistent.typing import PVector
from returns.io import IOFailure, IOSuccess
from returns.curry import curry


def _file_content(file: Path) -> IOResultAF[list[str]]:
    if not file.exists():
        return IOFailure(AppFailure.file_not_found)
    with open(file, "r") as f:
        return IOSuccess(f.readlines())


def _clear_newline(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines]


def file_lines(file: Path) -> IOResultAF[PVector[str]]:
    """
    Read the lines of a file and return them as a immutable list.
    """
    return _file_content(file).map(_clear_newline).map(freeze)


def create_file(file: Path, overwrite: bool = False) -> IOResultAF[None]:
    """
    Create a file.
    """
    if (not overwrite) and file.exists():
        return IOFailure(AppFailure.file_exists)
    with open(file, "w") as f:
        f.write("")
    return IOSuccess(None)


@curry
def write_file_lines(file: Path, lines: list[str]) -> IOResultAF[None]:
    """
    Write the lines to a file.
    """
    # check if file exists
    if not file.exists():
        return IOFailure(AppFailure.file_not_found)
    if file.is_dir():
        return IOFailure(AppFailure.write_to_dir)
    # check for write permissions
    if not file.stat().st_mode & 0o200:
        return IOFailure(AppFailure.file_read_only)

    with open(file, "w") as f:
        f.writelines("\n".join(lines))
        return IOSuccess(None)
