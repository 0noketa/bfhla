
from typing import cast, Tuple, Union, Optional
import config.bfhla as bfhla_config
from bfhla.struct import *
import bf.parser as bf_parser
import bf.analyser as bf_analyser


class IrScope:
    def __init__(self, name: str, size: Expr, base: Expr, offset: Expr, vars_: list[str], const_dic: dict[str, str] = {}):
        self.name = name
        self.size = size
        self.base = base
        self.offset = offset
        self.vars_ = vars_
        self.const_dict = self.const_dict

    @classmethod
    def from_decl(cls, args: ScopeDeclArgs) -> IrScope:
        return IrScope(args.name, args.size, args.base, args.offset, args.var_names())

class IrStep:
    def __init__(self, op: str, args: IArgs):
        self.op = op
        self.args = args

    def get_pair(self) -> Tuple[str, IArgs]:
        return self.op, self.args

    def __repr__(self):
        return f"Cmd({self.op}, {self.args})"


class Ir:
    def __init__(self, code: list[IrStep]) -> None:
        self.code = code
        self.default_type = "uint"
        self.default_array = "raw"
        self.default_assign = "copy"
        self.ip = 0
        self.address = 0
        self.at_unknown_address = False
        self.scopes: list[IrScope] = []
        self.last_result: tuple[str, ...] = []
        self.start()

    def load_default(self):
        self.default_type = "uint"
        self.default_array = "raw"
        self.default_assign = "copy"
        self.ip = 0
        self.address = 0
        self.at_unknown_address = False
        self.scopes = []
        self.last_result = tuple([])

    def start(self):
        self.load_default()

    def has_next_step(self) -> bool:
        return self.ip < len(self.code)

    def next_step(self):
        self.ip += 1

    def get_scope_index(self, name: str) -> int:
        return -1
        for i, scope in reversed(self.scopes):
            pass

    def get_var_index(self, name: str, scope_name: str = "") -> tuple[int, int]:
        """result: (var_index, scope_index)"""
        return -1, -1
        for i, scope in reversed(self.scopes):
            pass

    def current_op(self) -> str:
        return self.code[self.ip].get_pair()[0]

    def eval_step(self):
        op, args = self.code[self.ip].get_pair()

        if op == "scope":
            scope_args = cast(ScopeDeclArgs, args)
            scope = IrScope.from_decl(scope_args)
            self.scopes.append(scope)
        elif op == "at":
            addrs = cast(AddrSelectorArgs, args)
            sel = cast(Expr, addrs.addrs[0])

            if self.at_unknown_address:
                # fixme: even from unknown adress, "at" must be available on "$"-based expression.
                self.last_result = ("error", "unknown_address")
            elif sel.op == "signed":
                sel2 = cast(Expr, sel.args[1])
                n = int(sel2)
                if sel.args[0] == "-":
                    n = -n

                self.address += n
                self.last_result = ("success", "relative")
            else:
                var_name = "" # sel to str
                var_idx, scope_idx = self.get_var_index(var_name)
                self.last_result = ("success", "fixed", var_name)

