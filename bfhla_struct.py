
from typing import Tuple, Union
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

class ConstExpr:
    def __init__(self, op: str, args: list = None, value: Union[int, str] = 0):
        self.op = op
        self.args: list[ConstExpr] = args if args is not None else []
        self.value = value
    def is_num(self):
        return self.op == "num"
    def is_var(self, env: dict[str, int]):
        return self.op == "id" and self.value in env
    def is_id(self):
        return self.op == "id"
    def to_bfhla(self):
        if self.is_num() or self.is_id():
            return str(self.value)

        if len(self.args) == 2:
            arg0 = self.args[0].to_bfhla()
            arg1 = self.args[1].to_bfhla()
            if self.op == "+":
                return f"({arg0} + {arg1})"
            elif self.op == "-":
                return f"({arg0} - {arg1})"
            elif self.op == "*":
                return f"({arg0} * {arg1})"
            elif self.op == "/":
                return f"({arg0} / {arg1})"
            elif self.op == "%":
                return f"({arg0} % {arg1})"
        return f"{self.op}({' '.join(map(str, self.args))})"

    def calc(self, env: dict[str, int]):
        if len(self.args) == 2:
            arg0 = self.args[0]
            arg1 = self.args[1]
            arg0.calc(env)
            arg1.calc(env)

            v0 = None
            v1 = None
            if arg0.is_num() or arg0.is_var(env):
                v0 = int(arg0.args[0]) if arg0.is_num() else env[arg0.args[0]]
            if arg1.is_num() or arg1.is_var(env):
                v1 = int(arg1.args[0]) if arg1.is_num() else env[arg1.args[0]]

            if v0 is not None and v1 is not None:
                self.args = []
                if self.op == "+":
                    self.value = v0 + v1
                elif self.op == "-":
                    self.value = v0 - v1
                elif self.op == "*":
                    self.value = v0 * v1
                elif self.op == "/":
                    self.value = v0 // v1 if v1 != 0 else 0
                elif self.op == "%":
                    self.value = v0 % v1 if v1 != 0 else 0

    def __int__(self):
        if self.is_num():
            return int(self.value)

        if len(self.args) == 2:
            arg0 = int(self.args[0])
            arg1 = int(self.args[1])

            if self.op == "+":
                return arg0 + arg1
            elif self.op == "-":
                return arg0 - arg1
            elif self.op == "*":
                return arg0 * arg1
            elif self.op == "/":
                return arg0 // arg1 if arg1 != 0 else 0
            elif self.op == "%":
                return arg0 % arg1 if arg1 != 0 else 0

        return 0

    def __str__(self):
        return self.to_bfhla()

    def __repr__(self):
        return f"{self.op}({','.join(map(repr, self.args))})"

class Expr:
    def __init__(self, op: str, args: list = None, value: Union[int, str] = 0):
        self.op = op
        self.args: list[Expr] = args if args is not None else []
        self.value = value
    def is_num(self):
        return self.op == "num"
    def is_var(self, env: dict[str, int]):
        return self.op == "id" and self.value in env
    def is_id(self):
        return self.op == "id"
    def to_bfhla(self):
        if self.is_num() or self.is_id():
            return str(self.value)

        if len(self.args) == 2:
            arg0 = self.args[0].to_bfhla()
            arg1 = self.args[1].to_bfhla()
            if self.op == "+":
                return f"({arg0} + {arg1})"
            elif self.op == "-":
                return f"({arg0} - {arg1})"
            elif self.op == "*":
                return f"({arg0} * {arg1})"
            elif self.op == "/":
                return f"({arg0} / {arg1})"
            elif self.op == "%":
                return f"({arg0} % {arg1})"
        return f"{self.op}({' '.join(map(str, self.args))})"

    def calc(self, env: dict[str, int]):
        if len(self.args) == 2:
            arg0 = self.args[0]
            arg1 = self.args[1]
            arg0.calc(env)
            arg1.calc(env)

            v0 = None
            v1 = None
            if arg0.is_num() or arg0.is_var(env):
                v0 = int(arg0.args[0]) if arg0.is_num() else env[arg0.args[0]]
            if arg1.is_num() or arg1.is_var(env):
                v1 = int(arg1.args[0]) if arg1.is_num() else env[arg1.args[0]]

            if v0 is not None and v1 is not None:
                self.args = []
                if self.op == "+":
                    self.value = v0 + v1
                elif self.op == "-":
                    self.value = v0 - v1
                elif self.op == "*":
                    self.value = v0 * v1
                elif self.op == "/":
                    self.value = v0 // v1 if v1 != 0 else 0
                elif self.op == "%":
                    self.value = v0 % v1 if v1 != 0 else 0

    def __int__(self):
        if self.is_num():
            return int(self.value)

        if len(self.args) == 2:
            arg0 = int(self.args[0])
            arg1 = int(self.args[1])

            if self.op == "+":
                return arg0 + arg1
            elif self.op == "-":
                return arg0 - arg1
            elif self.op == "*":
                return arg0 * arg1
            elif self.op == "/":
                return arg0 // arg1 if arg1 != 0 else 0
            elif self.op == "%":
                return arg0 % arg1 if arg1 != 0 else 0

        return 0

    def __str__(self):
        return self.to_bfhla()

    def __repr__(self):
        return f"{self.op}({','.join(map(repr, self.args))})"

class RawArgs(IArgs):
    def __init__(self, args: dict = None):
        self.args = args
    def to_bfhla(self):
        return '"' + ", ".join(f"{k}: {v}" for k, v in self.args.items()) + '"'
    def __repr__(self):
        return f"RawArgs({self.args})"
class AssignArgs(IArgs):
    def __init__(self, dsts: list[LValue], src: Union[str, ConstExpr]):
        super().__init__()
        self.dsts = dsts
        self.src = src
    def to_bfhla(self):
        dst = ", ".join(map(LValue.to_bfhla, self.dsts))
        src = self.src.to_bfhla() if isinstance(self.src, ConstExpr) else self.src
        return f"{dst} = {src}"
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
    def __init__(self, name: str, size: ConstExpr, base: ConstExpr, offset: ConstExpr, vars: list[VarDecl]):
        super().__init__()
        self.name = name
        self.size = size
        self.base = base
        self.offset = offset
        self.vars = vars
    def is_relative(self):
        return not self.base.is_num()
    def var_names(self):
        return [i.name for i in self.vars]
    def __repr__(self):
        return f"ScopeDeclArgs(name={self.name}, size={self.size}, base={self.base}, offset={self.offset}, vars={self.vars})"




