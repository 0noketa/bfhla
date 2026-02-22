
from typing import Tuple
from bfhla_config import *


class IArgs:
    def __init__(self):
        pass
    def __repr__(self):
        return f"IArgs()"


class IrStep:
    def __init__(self, op: str, args: IArgs):
        self.op = op
        self.args = args

    def get_pair(self) -> Tuple[str, IArgs]:
        return self.op, self.args

    def __repr__(self):
        return f"Cmd({self.op}, {self.args})"

class LValue:
    def __init__(self, tkns: list[str], multiplier: int = 1, clear: bool = False):
        self.tkns = tkns
        self.multiplier = multiplier
        self.clear = clear

    def addr(self) -> str:
        return ''.join(self.tkns)

    def to_bfhla(self):
        s = self.addr()
        if self.multiplier == 0:
            return ""

        if self.multiplier == 1 and self.clear:
            return s

        if self.multiplier == 1:
            mul = "+"
        elif self.multiplier == -1:
            mul = "-"
        else:
            mul = f"{self.multiplier:+}"

        clear_op = "!" if self.clear else ""
        return f"{s}{clear_op}{mul}"

    def __repr__(self):
        return f"LValue(tkns={self.tkns}, multiplier={self.multiplier}, clear={self.clear})"


class RawArgs(IArgs):
    def __init__(self, args: dict = None):
        self.args = args
    def __repr__(self):
        return f"RawArgs({self.args})"
class AssignArgs(IArgs):
    def __init__(self, dsts: list[LValue], src: str):
        super().__init__()
        self.dsts = dsts
        self.src = src
    def to_bfhla(self):
        dst = ", ".join(map(LValue.to_bfhla, self.dsts))
        return f"{dst} = {self.src}"
    def __repr__(self):
        return f"AssignArgs(dsts={self.dsts}, src={self.src})"
class AddrSelectorArgs(IArgs):
    def __init__(self, addrs: list[str]):
        super().__init__()
        self.addrs = addrs
    def to_bfhla(self):
        return ", ".join(map(str, self.addrs))
    def __repr__(self):
        return f"AddrSelectorArgs(addrs={self.addrs})"
class ConfigArgs(IArgs):
    def __init__(self, name: str, value: str):
        super().__init__()
        self.name = name
        self.value = value
    def __repr__(self):
        return f"ConfigArgs(name={self.name}, value={self.value})"
class ScopeDeclArgs(IArgs):
    def __init__(self, name: str, size: int, base: int, offset: int, vars: list[str]):
        super().__init__()
        self.name = name
        self.size = size
        self.base = base
        self.offset = offset
        self.vars = vars
    def __repr__(self):
        return f"ScopeDeclArgs(name={self.name}, size={self.size}, base={self.base}, offset={self.offset}, vars={self.vars})"




class VarDecl:
    def __init__(self, name: str, type_: str = "uint"):
        self.name = name
        self.type = type_

    def __repr__(self):
        return f"{self.name}: {self.type}"

def var_name(addr: int) -> str:
    if addr < len(NAMED_VARS):
        return NAMED_VARS[addr]

    return f"{GLOBAL_SCOPE_NAME}[{addr}]"
