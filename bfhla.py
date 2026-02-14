from typing import Union
import sys
import re

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
class CmdTemplate:
    def __init__(self, op_: str, args_: list):
        self.op = op_
        self.args = args_
    def __repr__(self):
        return f"CmdTemplate({self.op}, [{','.join(map(repr, self.args))}])"
class ScopeTemplate:
    def __init__(self, name_: str, size_: Node, base_: Node, offset_: Node, vars_: list[Node]):
        self.name = name_
        self.size = size_
        self.base = base_
        self.offset = offset_
        self.vars = vars_
    def is_relative(self):
        return not self.base.is_num()
    def __repr__(self):
        return f"ScopeTemplate('{self.name}', {self.size}, {self.base}, {self.offset}, [{','.join(map(repr, self.vars))}])"
class Scope:
    def __init__(self, name_: str, size_: int, base_: Union[str, int], offset_: int, vars_: list[Node]):
        self.name = name_
        self.size = size_
        self.base = base_
        self.offset = offset_
        self.vars = vars_
    def is_relative(self):
        return not self.base.is_num()
    def __repr__(self):
        return f"Scope('{self.name}', {self.size}, {self.base}, {self.offset}, [{','.join(map(repr, self.vars))}])"
class Lex:
    @staticmethod
    def lex_lines(ss: list[str]) -> tuple[Union[str, tuple]]:
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
    def fold_blocks(tkns: list[str], block_right="(") -> tuple[tuple[Union[str, tuple]], int]:
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


def parse_line(tkns: tuple[Union[str, tuple]]) -> CmdTemplate:
    global current_base

    if tkns[0] == "config":
        if "=" not in tkns:
            cmd = CmdTemplate("error", [tkns])
        else:
            i = tkns.index("=")
            key = tkns[1]
            value = tkns[i + 1]
            config[key] = value
            cmd = CmdTemplate("config", [key, value])
    elif tkns[0] == "scope":
        scope = parse_scope(tkns[1:])
        cmd = CmdTemplate("scope", [scope])
    elif tkns[0] == "base":
        args = parse_args(tkns[1:])
        cmd = CmdTemplate("base", [args])
    elif tkns[0] == "at":
        args = parse_const_expr(tkns[1:])
        cmd = CmdTemplate("at", [args])
    elif tkns[0] == "offset":
        args = parse_const_expr(tkns[1:])
        cmd = CmdTemplate("offset", [args])
    elif tkns[0] == "bf":
        args = parse_const_expr(tkns[1:])
        cmd = CmdTemplate("bf", [args])
    elif tkns[0] == "bf_at":
        args = parse_const_expr(tkns[1:])
        cmd = CmdTemplate("bf_at", [args])
    elif tkns[0] == "expects":
        args = parse_const_expr(tkns[1:])
        cmd = CmdTemplate("expects", [args])
    elif tkns[0] == "init":
        args = parse_names(tkns[1:])
        cmd = CmdTemplate("init", args)
    elif tkns[0] == "clean":
        args = parse_names(tkns[1:])
        cmd = CmdTemplate("clean", args)
    elif tkns[0] in ["input", "print"]:
        args = parse_args(tkns[1:])
        cmd = CmdTemplate(tkns[0], [args])
    elif tkns[0] in ["copy", "move"]:
        args = parse_assign(tkns[1:], assign_method=tkns[0], is_move_args=True)
        cmd = CmdTemplate(tkns[0], [args])
    else:
        cmd = parse_assign(tkns)

    return cmd

def parse_scope_head(tkns: tuple[Union[str, tuple]]) -> tuple[str, Node, Node, Node]:
    name = ""
    size = None
    base = Node("id", ["__BASE__"])
    offset = Node("id", ["__OFFSET__"])

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
                base = Node("num", ["0"])
                offset = parse_const_expr(tkns)

    return name, size, base, offset
def parse_scope(tkns: tuple[Union[str, tuple]]) -> ScopeTemplate:
    if "=" in tkns:
        i = tkns.index("=")
        name, size, base, offset = parse_scope_head(tkns[:i])
        body = parse_var_decls(tkns[i+1:])
        return ScopeTemplate(name, size, base, offset, body)
    else:
        name, size, base, offset = parse_scope_head(tkns)
        body = parse_var_decls(tkns[1:])
        return ScopeTemplate(name, size, base, offset, body)

def parse_assign(tkns: tuple[Union[str, tuple]], assign_method:str=None, is_move_args: bool = False) -> CmdTemplate:
    if assign_method is None:
        assign_method = config["assign_method"]

    if "=" in tkns:
        i = tkns.index("=")
        src = parse_val(tkns[i+1:])
        dsts = parse_dsts(tkns[:i])
        return CmdTemplate(assign_method, [src, dsts])
    elif "->" in tkns:
        i = tkns.index("->")
        src = parse_val(tkns[:i])
        dsts = parse_dsts(tkns[i+1:])
        return CmdTemplate(assign_method, [src, dsts])
    elif is_move_args:
        args = parse_legacy_assign_args(tkns)
        src = parse_val(args[:1])
        dsts = parse_dsts(args[1:])
        return CmdTemplate(assign_method, [src, dsts])

    return CmdTemplate("error", [tkns])

def parse_legacy_assign_args(tkns: tuple[Union[str, tuple]]) -> list[Node]:
    args = []
    if "," in tkns:
        i = tkns.index(",")
        arg = parse_val(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    args.extend(parse_dsts(tkns))
    return args
def parse_args(tkns: tuple[Union[str, tuple]]) -> tuple[Node]:
    args = []
    while "," in tkns:
        i = tkns.index(",")
        arg = parse_val(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    arg = parse_val(tkns)
    args.append(arg)

    return tuple(args)
def parse_names(tkns: tuple[Union[str, tuple]]) -> tuple[Node]:
    args = []
    while "," in tkns[1:]:
        i = tkns.index(",")
        name = parse_const_qualified(tkns[:i])
        args.append(name)
        tkns = tkns[i+1:]

    name = parse_const_qualified(tkns)
    args.append(name)
    return tuple(args)
def parse_dsts(tkns: tuple[Union[str, tuple]]) -> list[Node]:
    args = []
    while "," in tkns:
        i = tkns.index(",")
        arg = parse_lval(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    arg = parse_lval(tkns)
    args.append(arg)

    return args

def parse_lval(tkns: tuple[Union[str, tuple]]) -> Node:
    if len(tkns) > 1:
        if tkns[-1] in ["+", "-"]:
            return Node("annotated", [tkns[-1], parse_val(tkns[:-1])])
    return parse_val(tkns)
def parse_val(tkns: tuple[Union[str, tuple]]) -> Node:
    if len(tkns) == 1:
        if tkns[0].isidentifier():
            return Node("id", [tkns[0]])
        elif tkns[0].isnumeric():
            return Node("num", [tkns[0]])
        elif tkns[0].startswith('"') and tkns[0].endswith('"'):
            return Node("str", [tkns[0][1: -1]])
        elif tkns[0] == "?":
            return Node("any", [])
        else:
            return Node("error", tkns)
    else:
        return Node("none", [])

def parse_var_decls(tkns: tuple[Union[str, tuple]]) -> list[Node]:
    args = []
    while "," in tkns:
        i = tkns.index(",")
        arg = parse_var_decl(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    arg = parse_var_decl(tkns)
    args.append(arg)

    return args
def parse_var_decl(tkns: tuple[Union[str, tuple]]) -> Node:
    if len(tkns) >= 1:
        if tkns[0].isidentifier():
            name = tkns[0]
            if len(tkns) > 2 and tkns[1] == ":":
                typ = parse_type(tkns[2:])
            else:
                typ = Node("type", [Node("primitive", [config["default_type"]])])
            return Node("var_decl", [name, typ])

    return Node("error", tkns)

def find_right_recur_opr(tkns: tuple[Union[str, tuple]], oprs: list[str]) -> tuple[str, int]:
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

def find_left_recur_opr(tkns: tuple[Union[str, tuple]], oprs: list[str]) -> tuple[str, int]:
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

def parse_const_expr(tkns: tuple[Union[str, tuple]]) -> Node:
    return parse_const_cmp(tkns)
def parse_const_cmp(tkns: tuple[Union[str, tuple]]) -> Node:
    if len(tkns) >= 3:
        opr, idx = find_left_recur_opr(tkns, ["==", "!=", ">", "<", ">=", "<="])
        if idx != -1:
            left = parse_const_cmp(tkns[:idx])
            right = parse_const_add(tkns[idx + 1:])
            if opr == "==":
                return Node("eq", [left, right])
            elif opr == "!=":
                return Node("neq", [left, right])
            elif opr == ">":
                return Node("gt", [left, right])
            elif opr == "<":
                return Node("lt", [left, right])
            elif opr == ">=":
                return Node("gte", [left, right])
            elif opr == "<=":
                return Node("lte", [left, right])

    return parse_const_add(tkns)
def parse_const_add(tkns: tuple[Union[str, tuple]]) -> Node:
    if len(tkns) >= 3:
        opr, idx = find_left_recur_opr(tkns, ["+", "-"])
        if idx != -1:
            left = parse_const_add(tkns[:idx])
            right = parse_const_mul(tkns[idx + 1:])
            if opr == "+":
                return Node("add", [left, right])
            elif opr == "-":
                return Node("sub", [left, right])

    return parse_const_mul(tkns)
def parse_const_mul(tkns: tuple[Union[str, tuple]]) -> Node:
    if len(tkns) >= 3:
        opr, idx = find_left_recur_opr(tkns, ["+", "/", "%"])
        if idx != -1:
            left = parse_const_mul(tkns[:idx])
            right = parse_const_qualified(tkns[idx + 1:])
            if opr == "*":
                return Node("mul", [left, right])
            elif opr == "/":
                return Node("div", [left, right])
            elif opr == "%":
                return Node("mod", [left, right])

    return parse_const_qualified(tkns)
def parse_const_qualified(tkns: tuple[Union[str, tuple]]) -> Node:
    if len(tkns) >= 3:
        _, idx = find_left_recur_opr(tkns, ["."])
        if idx != -1:
            left = parse_const_qualified(tkns[:idx])
            right = parse_const_val(tkns[idx + 1:])
            return Node(".", [left, right])
    elif len(tkns) >= 2 and type(tkns[-1]) == tuple:
        base = parse_const_qualified(tkns[:-1])
        index = parse_const_expr(tkns[-1])
        return Node("[]", [base, index])

    return parse_const_val(tkns)
def parse_const_val(tkns: tuple[Union[str, tuple]]) -> Node:
    if len(tkns) == 1:
        if tkns[0].isidentifier():
            return Node("id", [tkns[0]])
        elif tkns[0].isnumeric():
            return Node("num", [tkns[0]])
        elif tkns[0].startswith('"') and tkns[0].endswith('"'):
            return Node("str", [tkns[0][1: -1]])

    return Node("error", tkns)

def parse_type(tkns: tuple[Union[str, tuple]]) -> Node:
    if len(tkns) >= 1:
        if type(tkns[-1]) == tuple:
            array_len = parse_const_expr(tkns[-1])
            if len(tkns) == 1:
                elm_type = Node("primitive", [config["default_type"]])
            else:
                elm_type = parse_type(tkns[:-1])
            return Node("array", [array_len, elm_type, config["default_array_type"]])
        if tkns[0].isidentifier():
            name = tkns[0]
            return Node("primitive", [name])

    return Node("error", tkns)



src = sys.stdin.readlines()
src = Lex.lex_lines(src)
print(src)
for line in src:
    print(line)
    cmd = parse_line(line)
    print(cmd)

for scope_name in scopes:
    print(scope_name, scopes[scope_name])