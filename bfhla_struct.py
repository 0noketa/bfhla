
from typing import Tuple
from bfhla_config import *


class IrStep:
    def __init__(self, op: str, args: dict):
        self.op = op
        self.args = args

    def get_pair(self) -> Tuple[str, dict]:
        return self.op, self.args


def var_name(addr: int) -> str:
    if addr < len(NAMED_VARS):
        return NAMED_VARS[addr]

    return f"{GLOBAL_SCOPE_NAME}[{addr}]"
