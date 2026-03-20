
from typing import Tuple, Union, Optional
import config.bfhla as bfhla_config
import bf.parser as bf_parser
import bf.analyser as bf_analyser


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

    def has_clear(self):
        return self.clear

    def addr(self) -> str:
        i = 0
        s = ""
        src = self.tkns
        stk = []

        while i < len(src) or len(stk) > 0:
            if i >= len(src):
                s += "]"
                i, src = stk.pop()
                continue

            tkn = src[i]
            i += 1

            if type(tkn) == str:
                s += tkn
            elif type(tkn) == tuple:
                s += "["
                stk.append((i + 1, src))
                src = tkn
                i = 0

        return s

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
    if addr < len(bfhla_config.disasm.named_vars):
        return bfhla_config.disasm.named_vars[addr]

    return f"{bfhla_config.disasm.global_scope_name}[{addr}]"

class Expr:
    @classmethod
    def num_node(cls, n: str):
        return Expr("num", value=n)
    @classmethod
    def str_node(cls, s: str):
        return Expr("str", value=s)
    @classmethod
    def id_node(cls, id: str):
        return Expr("id", value=id)

    def __init__(self, op: str, args: Optional[list] = None, value: Union[int, str] = 0):
        self.op = op
        self.args: list[Expr] = args if args is not None else []
        self.value = value
    def is_num(self):
        return self.op == "num"
    def is_var(self, env: dict[str, int]):
        return self.op == "id" and self.value in env
    def is_id(self):
        return self.op == "id"
    def is_str(self):
        return self.op == "str"
    def is_const(self):
        return self.is_num() or self.is_id() or self.is_str()
    def to_bfhla(self):
        if self.is_const():
            return str(self.value)

        if self.op == "signed":
            return self.args[0].to_bfhla() + self.args[1].to_bfhla()

        if self.op == "indexed":
            return self.args[0].to_bfhla() + "[" + self.args[1].to_bfhla() + "]"

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

            v0: Union[int, None] = None
            v1: Union[int, None] = None
            if arg0.is_num():
                v0 = int(arg0.args[0])
            elif arg0.is_var(env):
                v0 = env[arg0.args[0].value]
            if arg1.is_num():
                v1 = int(arg1.args[0])
            elif arg1.is_var(env):
                v1 = env[arg1.args[0].value]

            if v0 is not None and v1 is not None:
                self.args = []
                if self.op == "+":
                    self.op = "num"
                    self.value = v0 + v1
                elif self.op == "-":
                    self.op = "num"
                    self.value = v0 - v1
                elif self.op == "*":
                    self.op = "num"
                    self.value = v0 * v1
                elif self.op == "/":
                    self.op = "num"
                    self.value = v0 // v1 if v1 != 0 else 0
                elif self.op == "%":
                    self.op = "num"
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

    def decoded_str(self) -> str:
        if self.op == "str":
            return self.value
        return "<error_str>"

    def __str__(self):
        return self.to_bfhla()

    def __repr__(self):
        return f"{self.op}({','.join(map(repr, self.args))})"

class RawArgs(IArgs):
    def __init__(self, args: Optional[dict] = None):
        self.args = args
    def to_bfhla(self):
        return '"' + ", ".join(f"{k}: {v}" for k, v in self.args.items()) + '"'
    def __repr__(self):
        return f"RawArgs({self.args})"
class BfArgs(IArgs):
    def __init__(self, bf: list[tuple[str, int]]):
        s = bf_analyser.bfir_to_bf(bf)
        self.bf: list[tuple[str, int]] = bf_parser.bf_to_bfir(s)
    def to_bfhla(self):
        return bf_analyser.bfir_to_bfrle(self.bf)
    def __repr__(self):
        return f"BfArgs(text={self.to_bfhla()!r})"
class AssignArgs(IArgs):
    def __init__(self, dsts: list[LValue], src: Expr):
        super().__init__()
        self.dsts = dsts
        self.src = src
    def to_bfhla(self):
        dst = ", ".join(map(LValue.to_bfhla, self.dsts))
        src = self.src.to_bfhla() if isinstance(self.src, Expr) else self.src
        return f"{dst} = {src}"
    def __repr__(self):
        return f"AssignArgs(dsts={self.dsts}, src={self.src})"
class AddrSelectorArgs(IArgs):
    def __init__(self, addrs: list[Expr]):
        super().__init__()
        self.addrs = addrs
    def to_bfhla(self):
        return ", ".join(map(Expr.to_bfhla, self.addrs))
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
    def __init__(self, name: str, size: Expr, base: Expr, offset: Expr, vars: list[VarDecl]):
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




