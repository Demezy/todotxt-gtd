from typing import Any
from returns.io import impure
from returns.functions import tap
from rich import print
from rich.pretty import pprint


__all__ = ["ioinput", "ioprint", "iopprint"]


# mypy fail to detemine type, so...
def _pprint_wrapper(x: Any) -> None:
    pprint(x, expand_all=True)


ioinput = impure(input)
ioprint = impure(tap(print))
iopprint = impure(tap(_pprint_wrapper))
