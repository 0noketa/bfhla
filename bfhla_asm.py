from typing import cast, Union
import re
import bfhla_config
from bfhla_struct import *


lex = re.compile("""\\s*(
    "(?:[^"]|\\")*"
    |[0-9]+
    |[a-zA-Z_][a-zA-Z0-9_]*
    |==
    |!=
    |>=
    |<=
    |\\->
    |<\\-
    |[+\\-*/%^&\\|@\\$\\?\\:!><,.\\[\\]\\{\\}\\(\\)=]
    |\\#
)""".replace(" ", "").replace("\n", "").replace("\r", ""))

def list_last_index(lst: list, x):
    if x in lst:
        return len(lst) - 1 - list(reversed(lst)).index(x)

    return -1

class Node:
    def __init__(self, op_: str, args_: list):
        self.op = op_
        self.args = args_
    def is_num(self):
        return self.op == "num"
    def __int__(self):
        if self.is_num():
            return int(self.args[0])
        else:
            return -1
    def __repr__(self):
        return f"{self.op}({','.join(map(repr, self.args))})"

class Lex:
    @staticmethod
    def lex_lines(ss: list[str]) -> tuple[Union[str, tuple], ...]:
        dst = []
        for s in ss:
            tkns = lex.findall(s)
            tkns = Lex.remove_comment(tkns)
            tkns, _ = Lex.fold_blocks(tkns)
            if tkns:
                dst.append(tkns)

        return tuple(dst)

    @staticmethod
    def remove_comment(tkns: list[str]) -> list[str]:
        if "#" in tkns:
            i = tkns.index("#")
            tkns = tkns[:i]

        return tkns
    @staticmethod
    def block_left_by_right(s: str) -> str:
        return {"(": ")", "[": "]", "{": "}"}[s]
    @staticmethod
    def fold_blocks(tkns: list[str], block_right="(") -> tuple[tuple[Union[str, tuple], ...], int]:
        """last step. this method turns lists into tuples"""
        block_left = Lex.block_left_by_right(block_right)
        dst = []
        i = 0
        while i < len(tkns):
            tkn = tkns[i]

            if tkn in ("(", "[", "{"):
                block, j = Lex.fold_blocks(tkns[i + 1:], tkn)
                dst.append(block)
                i += j + 1
                continue
            elif tkn == block_left:
                return tuple(dst), i + 1
            elif tkn in (")", "]", "}"):
                # error
                return tuple(dst), i + 1

            dst.append(tkn)
            i += 1

        return tuple(dst), i


current_base = 0
current_offset = 0
scopes = {}
config = {
    "assign_method": "copy",
    "default_type": "uint",
    "default_array_type": "raw_array",
}


def parse_line(tkns: tuple[Union[str, tuple], ...]) -> IrStep:
    global current_base

    if tkns[0] == "config":
        if "=" not in tkns:
            cmd = IrStep("error", RawArgs({"src": tkns}))
        else:
            i = tkns.index("=")
            if i < 2 or i >= len(tkns) - 1:
                cmd = IrStep("error", RawArgs({"src": tkns}))
            else:
                key = tkns[1]
                value = tkns[i + 1]
                config[key] = value
                cmd = IrStep("config", ConfigArgs(name=key, value=value))
    elif tkns[0] == "scope":
        scope = parse_scope(tkns[1:])
        cmd = IrStep("scope", scope)
    elif tkns[0] == "at":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("at", AddrSelectorArgs([args]))
    elif tkns[0] == "bf":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("bf", BfArgs(args.decoded_str()))
    elif tkns[0] == "bf_at":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("bf_at", BfArgs(args.decoded_str()))
    elif tkns[0] == "expects":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("expects", RawArgs({"code": args}))
    elif tkns[0] == "skipr":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("skipr", AddrSelectorArgs([args]))
    elif tkns[0] == "skipl":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("skipl", AddrSelectorArgs([args]))
    elif tkns[0] == "ifnz":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("ifnz", AddrSelectorArgs([args]))
    elif tkns[0] == "predec_for":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("predec_for", AddrSelectorArgs([args]))
    elif tkns[0] == "postdec_for":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("postdec_for", AddrSelectorArgs([args]))
    elif tkns[0] == "balanced_loop_at":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("balanced_loop_at", AddrSelectorArgs([args]))
    elif tkns[0] == "balanced_loop":
        cmd = IrStep("balanced_loop", RawArgs({}))
    elif tkns[0] == "loop":
        cmd = IrStep("loop", RawArgs({}))
    elif tkns[0] == "end":
        cmd = IrStep("end", RawArgs({}))
    elif tkns[0] == "init":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("init", AddrSelectorArgs([args]))
    elif tkns[0] == "clean":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("clean", AddrSelectorArgs([args]))
    elif tkns[0] == "clear":
        args = parse_const_expr(tkns[1:])
        cmd = IrStep("clear", AddrSelectorArgs([args]))
    elif tkns[0] in ["input", "print"]:
        args = parse_const_expr(tkns[1:])
        cmd = IrStep(tkns[0], AddrSelectorArgs([args]))
    else:
        if tkns[0] in ["copy", "move"]:
            # args = parse_assign(tkns[1:], assign_method=tkns[0], is_move_args=True)
            # cmd = IrStep(tkns[0], AssignArgs(args.args.dst, args.args.src))
            cmd = parse_assign(tkns[1:], assign_method=tkns[0], is_move_args=True)
        else:
            cmd = parse_assign(tkns)

        if cmd.op in ["copy", "move"] and type(cmd.args) is AssignArgs and len(cmd.args.dsts) == 0:
            cmd = IrStep("clear", AddrSelectorArgs([cmd.args.src]))


    return cmd

def parse_scope_head(tkns: tuple[Union[str, tuple], ...]) -> tuple[str, Expr, Expr, Expr]:
    name = ""
    size = None
    base = Expr.id_node("__BASE__")
    offset = Expr.id_node("__OFFSET__")

    if len(tkns) >= 1 and type(tkns[0]) is str and tkns[0].isidentifier():
        name = tkns[0]
    if len(tkns) >= 2 and (type(tkns[1]) is not str or tkns[1] == "@"):
        if len(tkns) >= 2 and type(tkns[1]) is tuple:
            size = parse_const_expr(tkns[1])
        if len(tkns) >= 2 and ("@" in tkns):
            i = tkns.index("@")
            tkns = tkns[i + 1:]
            if "+" in tkns:
                i = tkns.index("+")
                base = parse_const_qualified(tkns[:i])
                offset = parse_const_expr(tkns[i + 1:])
            else:
                base = Expr.num_node("0")
                offset = parse_const_expr(tkns)

    return name, size, base, offset
def parse_scope(tkns: tuple[Union[str, tuple], ...]) -> ScopeDeclArgs:
    if "=" in tkns:
        i = tkns.index("=")
        name, size, base, offset = parse_scope_head(tkns[:i])
        body = parse_var_decls(tkns[i+1:])
        return ScopeDeclArgs(name, size, base, offset, body)
    else:
        name, size, base, offset = parse_scope_head(tkns)
        body = parse_var_decls(tkns[1:])
        return ScopeDeclArgs(name, size, base, offset, body)

def parse_assign(tkns: tuple[Union[str, tuple], ...], assign_method:str=None, is_move_args: bool = False) -> IrStep:
    if assign_method is None:
        assign_method = config["assign_method"]

    if "=" in tkns:
        i = tkns.index("=")
        src = parse_val(tkns[i+1:])
        dsts = parse_dsts(tkns[:i])
        return IrStep(assign_method, AssignArgs(dsts, src))
    elif "->" in tkns:
        i = tkns.index("->")
        src = parse_val(tkns[:i])
        dsts = parse_dsts(tkns[i+1:])
        return IrStep(assign_method, AssignArgs(dsts, src))
    elif is_move_args:
        args = parse_legacy_assign_args(tkns)
        src = parse_val(args[:1])
        dsts = parse_dsts(args[1:])
        return IrStep(assign_method, AssignArgs(dsts, src))

    return IrStep("error", RawArgs({"src": tkns}))

def parse_legacy_assign_args(tkns: tuple[Union[str, tuple], ...]) -> list[Node]:
    args = []
    if "," in tkns:
        i = tkns.index(",")
        arg = parse_val(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    args.extend(parse_dsts(tkns))
    return args
def parse_args(tkns: tuple[Union[str, tuple], ...]) -> tuple[Node]:
    args = []
    while "," in tkns:
        i = tkns.index(",")
        arg = parse_val(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    arg = parse_val(tkns)
    args.append(arg)

    return tuple(args)
def parse_names(tkns: tuple[Union[str, tuple], ...]) -> tuple[Node]:
    args = []
    while "," in tkns[1:]:
        i = tkns.index(",")
        name = parse_const_qualified(tkns[:i])
        args.append(name)
        tkns = tkns[i+1:]

    name = parse_const_qualified(tkns)
    args.append(name)
    return tuple(args)
def parse_dsts(tkns: tuple[Union[str, tuple], ...]) -> list[LValue]:
    args = []
    while "," in tkns:
        i = tkns.index(",")
        arg = parse_lval(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    arg = parse_lval(tkns)
    args.append(arg)

    return args

def parse_lval(tkns: tuple[Union[str, tuple], ...]) -> LValue:
    if len(tkns) > 1 and type(tkns[-1]) is str:
        if tkns[-1] in ["+", "-"]:
            sign = 1 if tkns[-1] == "+" else -1
            return LValue(tkns[:-1], multiplier=sign)
        elif len(tkns) > 2 and type(tkns[-2]) is str and tkns[-2] in ["+", "-"]:
            sign = 1 if tkns[-2] == "+" else -1
            sign *= int(tkns[-1])
            return LValue(tkns[:-2], multiplier=sign)
    return LValue(tkns, clear=True)
def parse_val(tkns: tuple[Union[str, tuple], ...]) -> Expr:
    if len(tkns) == 1 and type(tkns[0]) is str:
        if tkns[0].isidentifier() or tkns[0] == "$":
            return Expr.id_node(tkns[0])
        elif tkns[0].isnumeric():
            return Expr.num_node(tkns[0])
        elif tkns[0].startswith('"') and tkns[0].endswith('"'):
            return Expr.str_node(tkns[0][1: -1])
        elif tkns[0] == "?":
            return Expr("any", value="?")
        else:
            return Expr("error", value=f"{tkns}")
    elif (len(tkns) == 2
            and type(tkns[0]) is str
            and (tkns[0].isidentifier() or tkns[0] == "$")):
        id = Expr.id_node(tkns[0])
        idx = parse_const_expr(cast(tuple[Union[str, tuple], ...], tkns[1]))
        return Expr("indexed", [id, idx])
    else:
        return Expr("none", value="none")

def parse_var_decls(tkns: tuple[Union[str, tuple], ...]) -> list[VarDecl]:
    args = []
    while "," in tkns:
        i = tkns.index(",")
        arg = parse_var_decl(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    arg = parse_var_decl(tkns)
    args.append(arg)

    return args
def parse_var_decl(tkns: tuple[Union[str, tuple], ...]) -> VarDecl:
    if len(tkns) >= 1:
        tkn = cast(str, tkns[0])
        if tkn.isidentifier():
            name = tkn
            # if len(tkns) > 2 and tkns[1] == ":":
            #     typ = parse_type(tkns[2:])
            # else:
            #     typ = Node("type", [Node("primitive", [config["default_type"]])])
            typ = config["default_type"]
            return VarDecl(name, typ)

    return VarDecl("error", f"<error_type: {tkns}>")

def find_right_recur_opr(tkns: tuple[Union[str, tuple], ...], oprs: list[str]) -> tuple[str, int]:
    indices = []
    for opr in oprs:
        try:
            idx = tkns.index(opr)
        except:
            idx = len(tkns)
        indices.append(idx)

    min_idx = min(*indices)
    if min_idx == len(tkns):
        return "", -1

    opr_idx = indices.index(min_idx)
    return oprs[opr_idx], min_idx

def find_left_recur_opr(tkns: tuple[Union[str, tuple], ...], oprs: list[str]) -> tuple[str, int]:
    indices = []
    for opr in oprs:
        try:
            idx = list_last_index(tkns, opr)
        except:
            idx = -1
        indices.append(idx)

    max_idx = max(*indices) if len(indices) > 1 else indices[0]
    if max_idx == -1:
        return "", -1

    opr_idx = indices.index(max_idx)
    return oprs[opr_idx], max_idx

def parse_const_expr(tkns: tuple[Union[str, tuple], ...]) -> Expr:
    return parse_const_cmp(tkns)
def parse_const_cmp(tkns: tuple[Union[str, tuple], ...]) -> Expr:
    if len(tkns) >= 3:
        opr, idx = find_left_recur_opr(tkns, ["==", "!=", ">", "<", ">=", "<="])
        if idx != -1:
            left = parse_const_cmp(tkns[:idx])
            right = parse_const_add(tkns[idx + 1:])
            if opr == "==":
                return Expr("==", [left, right])
            elif opr == "!=":
                return Expr("!=", [left, right])
            elif opr == ">":
                return Expr(">", [left, right])
            elif opr == "<":
                return Expr("<", [left, right])
            elif opr == ">=":
                return Expr(">=", [left, right])
            elif opr == "<=":
                return Expr("<=", [left, right])

    return parse_const_add(tkns)
def parse_const_add(tkns: tuple[Union[str, tuple], ...]) -> Expr:
    if len(tkns) >= 3:
        opr, idx = find_left_recur_opr(tkns, ["+", "-"])
        if idx != -1:
            left = parse_const_add(tkns[:idx])
            right = parse_const_mul(tkns[idx + 1:])
            if opr == "+":
                return Expr("+", [left, right])
            elif opr == "-":
                return Expr("-", [left, right])

    return parse_const_mul(tkns)
def parse_const_mul(tkns: tuple[Union[str, tuple], ...]) -> Expr:
    if len(tkns) >= 3:
        opr, idx = find_left_recur_opr(tkns, ["*", "/", "%"])
        if idx != -1:
            left = parse_const_mul(tkns[:idx])
            right = parse_const_qualified(tkns[idx + 1:])
            if opr == "*":
                return Expr("*", [left, right])
            elif opr == "/":
                return Expr("/", [left, right])
            elif opr == "%":
                return Expr("%", [left, right])

    return parse_const_qualified(tkns)
def parse_const_qualified(tkns: tuple[Union[str, tuple], ...]) -> Expr:
    if len(tkns) >= 3:
        _, idx = find_left_recur_opr(tkns, ["."])
        if idx != -1:
            left = parse_const_qualified(tkns[:idx])
            right = parse_const_val(tkns[idx + 1:])
            return Expr(".", [left, right])
    elif len(tkns) >= 2 and type(tkns[-1]) == tuple:
        base = parse_const_qualified(tkns[:-1])
        index = parse_const_expr(tkns[-1])
        return Expr("[]", [base, index])

    return parse_const_val(tkns)
def parse_const_val(tkns: tuple[Union[str, tuple], ...]) -> Expr:
    if len(tkns) == 1:
        tkn = cast(str, tkns[0])
        if type(tkn) == tuple:
            return parse_const_expr(tkn)
        if tkn.isidentifier():
            return Expr.id_node(tkn)
        elif tkn.isnumeric():
            return Expr.num_node(tkn)
        elif len(tkn) >= 2 and tkn.startswith('"') and tkn.endswith('"'):
            return Expr.str_node(tkn[1: -1])

    if len(tkns) == 2:
        if type(tkns[0]) == str and tkns[0] in ["+", "-"]:
            return Expr("signed", [tkns[0], parse_const_expr(tkns[1:])])

    return Expr("error", value=f"{tkns}")

def parse_type(tkns: tuple[Union[str, tuple], ...]) -> Node:
    if len(tkns) >= 1:
        if type(tkns[-1]) == tuple:
            array_len = parse_const_expr(tkns[-1])
            if len(tkns) == 1:
                elm_type = Node("primitive", [config["default_type"]])
            else:
                elm_type = parse_type(tkns[:-1])
            return Node("array", [array_len, elm_type, config["default_array_type"]])
        if type(tkns[0]) == str and tkns[0].isidentifier():
            name = tkns[0]
            return Node("primitive", [name])

    return Node("error", [f"{tkns}"])



if __name__ == "__main__":
    import sys

    target = "bfhla"

    for arg in sys.argv:
        if arg.startswith("-t"):
            target = arg[2:]
        elif arg.startswith("--no_semantic_analyser"):
            bfhla_config.disasm.replace("no_semantic_analyser", True)
        elif arg.startswith("--indent_unit="):
            bfhla_config.codegen.replace("indent_unit", arg[len("--indent_unit="):])
        elif arg.startswith("--max_inline_bf_length="):
            bfhla_config.codegen.replace("max_inline_bf_length", int(arg[len("--max_inline_bf_length="):]))
        elif arg.startswith("--no_bfrle"):
            bfhla_config.codegen.replace("no_bfrle", True)
        elif arg.startswith("--buf_size="):
            bfhla_config.disasm.replace("buf_size", int(arg[len("--buf_size="):]))
        elif arg.startswith("--global_scope_name="):
            bfhla_config.disasm.replace("global_scope_name", arg[len("--global_scope_name="):])
        elif arg in ["-h", "--help"]:
            print("usage: bfhla_asm.py [options] < input.bfhla > output")
            print("options:")
            print("  -tTARGET, --target=TARGET    set target (default: bfhla)")
            print("  --no_semantic_analyser       outputs only raw loops")
            print("  --indent_unit=UNIT           set indent unit (default: 4 spaces)")
            print("  --max_inline_bf_length=N     merges inline BF until this length (default: 64)")
            print("  --no_bfrle                   disables BF-RLE(suffix) as inline BF")
            print("  --buf_size=N                 set buffer size for disasm (default: 32767)")
            print("  --global_scope_name=NAME     set global scope name for disasm (default: mem)")
            print("  -h, --help                   show this help message and exit")
            print("targets: bfhla, bf, c")
            sys.exit(0)

    src = sys.stdin.readlines()
    src = Lex.lex_lines(src)

    prog = []
    for line in src:
        # print(f"# {line}")
        cmd = parse_line(line)
        # print(f"# {cmd}")
        prog.append(cmd)

    if target == "bfhla":
        import codegen_bfhla
        codegen_bfhla.print_bfhla(prog)
    elif target == "bf":
        import codegen_bf
        codegen_bf.print_bf(prog)
    elif target == "c":
        import codegen_c
        codegen_c.print_c(prog)
    else:
        print(f"unknown target: {target}")
