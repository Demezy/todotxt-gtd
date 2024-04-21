from enum import Enum

from pyrsistent import freeze


CONTEXTS = freeze(
    {
        "t": "_TODO",
        "s": "_SOMEDAY",
        "c": "_CALENDAR",
        "w": "_WAITING",
        "p": "_PROJECTS",
        "d": "_DONE",
        "n": "_NOTES",
    }
)

PROJECTS = freeze(
    {
        "p": "project1",
    }
)


class Priority(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
