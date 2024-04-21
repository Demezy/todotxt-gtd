from returns.io import impure
from returns.functions import tap
from rich import print
from rich.pretty import pprint


__all__ = ["input", "ioprint", "iopprint"]

input = impure(input)
ioprint = impure(tap(print))
iopprint = impure(tap(lambda x: pprint(x, expand_all=True)))
