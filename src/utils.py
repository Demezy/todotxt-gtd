from enum import Enum
from typing import Callable, Iterable, Type, TypeVar

from flupy import flu
from pyrsistent import PMap, PVector, pvector
from returns.maybe import Maybe, Nothing, Some, maybe
from returns.io import IO, IOResult
from returns.unsafe import unsafe_perform_io

from returns.result import Result, Success
from returns.curry import curry
from returns.iterables import Fold


K = TypeVar("K")  # Key type
V = TypeVar("V")  # Value type
E = TypeVar("E", bound=Enum)  # Enum type
F = TypeVar("F")  # Failure type
T = TypeVar("T")  # argument type
R = TypeVar("R")  # Result type


def maybe_get_map(map: PMap[K, V], key: K) -> Maybe[V]:
    """
    Get the value from the map if it exists, otherwise return Nothing
    """
    return maybe(map.get)(key)


def maybe_get_enum(enum: Type[E], key: str) -> Maybe[E]:
    """
    Get the enum value from the key if it exists, otherwise return Nothing
    """
    try:
        return Some(enum[key])
    except KeyError:
        return Nothing


def recovered_result(recovery: Callable[[F], T], result: Result[T, F]) -> T:
    return result.lash(lambda failure: Success(recovery(failure))).unwrap()


@curry
def push_back(item: T, accumulator: PVector[T]) -> PVector[T]:
    return accumulator.append(item)


def io_vector(ios: Iterable[IO[T]]) -> IO[PVector[T]]:
    acc: PVector[T] = pvector()  # help mypy to detemine types
    return Fold.loop(ios, IO(acc), push_back)


def flatten_io_result(result: IOResult[IO[T], F]) -> IOResult[T, F]:
    return result.map(unsafe_perform_io)


def flatten_result_io(io: IO[IOResult[T, F]]) -> IOResult[T, F]:
    return unsafe_perform_io(io)


# endofunctor
def conditional_map(
    predicate: Callable[[T], bool], transformer: Callable[[T], T], iterable: Iterable[T]
) -> PVector[T]:
    return pvector(map(lambda x: transformer(x) if predicate(x) else x, iterable))


@curry
def pfilter(
    predicate: Callable[[T], bool],
    tasks: PVector[T],
) -> PVector[T]:
    return pvector(filter(predicate, tasks))


def result_recovered(recovery: Callable[[F], IO[T]], result: IOResult[T, F]) -> IO[T]:
    return result.lash(lambda failure: IOResult.from_io(recovery(failure))).unwrap()


def result_io_flatmap(
    result_xs: IOResult[Iterable[T], F],
    mapper: Callable[[T], IO[R]],
) -> IOResult[PVector[R], F]:
    mapped_xs = result_xs.map(lambda xs: flu(xs).map(mapper))
    io_sequence = mapped_xs.map(lambda io_xs: io_vector(io_xs))
    return flatten_io_result(io_sequence)


# def rail_print(message: str) -> Callable[[T], IO[T]]:  # type[T@rail_print]
#     def _rail_print(value: T) -> IO[T]:  # type[T@_rail_print]
#         print(message)
#         return IO(value)

#     return _rail_print


# Using a lambda to ensure each element from range(5) is passed correctly to the returned function from rail_print
# b = list(map(rail_print("message"), range(5)))
# a = list(map(lambda x: rail_print("message")(x), range(5)))

# Since rail_print("message") itself does not directly return a function that is ready to be used with map,
# we can directly invoke the returned function in the map call like this:
# a = [rail_print("message")(i) for i in range(5)]

# for item in a:
#     print(item._inner_value)
