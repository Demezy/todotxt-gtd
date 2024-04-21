from enum import Enum
from typing import TypeVar, assert_never

from returns import io
from returns import result
from returns import future


class AppFailure(Enum):
    file_not_found = "file_not_found"
    file_read_only = "file_read_only"
    unknown_fs_error = "unknown_fs_error"
    write_to_dir = "write_to_dir"
    file_exists = "file_exists"
    test = "test"  # added for testing and debug purposes


_ValueType = TypeVar("_ValueType", covariant=True)

IOResultAF = io.IOResult[_ValueType, AppFailure]
ResultAF = result.Result[_ValueType, AppFailure]
FutureResultAF = future.FutureResult[_ValueType, AppFailure]


def handle_failure(failure: AppFailure) -> io.IO[None]:
    """
    Automagically handle failures
    """
    # TODO: implement
    match failure:
        case (
            AppFailure.file_not_found
            | AppFailure.file_read_only
            | AppFailure.unknown_fs_error
            | AppFailure.write_to_dir
        ):
            return io.IO(None)
        case AppFailure.test:
            return io.IO(None)
        case _:
            assert_never(failure)
