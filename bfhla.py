import sys
import re

lex = re.compile("""\\s*(
    "(?:[^"]|\\")*"
    |[0-9]+
    |[a-zA-Z_][a-zA-Z0-9_]*
    |[+\\-*/%^&\\|@\\$\\?\\:!><,.\\[\\]\\{\\}\\(\\)=]
    |==
    |!=
    |\\->
    |<\\-
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
    def __repr__(self):
        return f"Node({self.op}, [{','.join(map(repr, self.args))}])"
class Cmd:
    def __init__(self, op_: str, args_: list):
        self.op = op_
        self.args = args_
    def __repr__(self):
        return f"Cmd({self.op}, [{','.join(map(repr, self.args))}])"
class Scope:
    def __init__(self, name_: str, offset_: int, args_: list, base_ = 0):
        self.name = name_
        self.base = base_
        self.offset = offset_
        self.args = args_
    def is_relative(self):
        return self.base != 0
    def __repr__(self):
        return f"Scope({self.name}, {self.base}, [{','.join(map(repr, self.args))}])"

current_base = 0
current_offset = 0
scopes = {}
config = {
    "assign_method": "copy",
    "default_type": "uint",
}

def parse_line(s: str):
    global current_base
    tkns = lex.findall(s)
    if "#" in tkns:
        i = tkns.index("#")
        tkns = tkns[:i]

    if len(tkns) == 0:
        return Cmd("empty", [])

    if tkns[0] == "config":
        key = tkns[1]
        value = tkns[2]
        if key == "assign_method":
            config["assign_method"] = value
        elif key == "default_type":
            config["default_type"] = value
        return Cmd("config", [key, value])
    elif tkns[0] == "scope":
        scope_name = tkns[1]
        members = parse_var_decls(tkns[2:])
        cmd = Cmd("scope", [scope_name, members])
        scopes[scope_name] = Scope(scope_name, current_offset, members, base_=current_base)
    elif tkns[0] == "base":
        args = parse_args(tkns)
        if len(args) == 0:
            cmd = Cmd("base", [])
        else:
            if args[0].op == "num":
                current_base = int(args[0].args[0])
            elif args[0].op == "id" and args[0].args[0] in scopes:
                current_base = scopes[args[0].args[0]].base
            elif args[0].op == "any":
                current_base = "?"
            cmd = Cmd("base", [args])
    elif tkns[0] in ["input", "print"]:
        scope_name = tkns[1]
        args = parse_args(tkns[1:])
        cmd = Cmd(tkns[0], [args])
    elif tkns[0] in ["copy", "move"]:
        scope_name = tkns[1]
        args = parse_assign(tkns[1:], assign_method=tkns[0], is_move_args=True)
        cmd = Cmd(tkns[0], [args])
    else:
        cmd = parse_assign(tkns)

    return cmd

def parse_assign(tkns: list[str], assign_method:str=None, is_move_args: bool = False) -> list[str]:
    if assign_method is None:
        assign_method = config["assign_method"]

    if "=" in tkns:
        i = tkns.index("=")
        src = tkns[i+1:]
        dsts = parse_dsts(tkns[:i])
        return Cmd(assign_method, [src, dsts])
    elif "->" in tkns:
        i = tkns.index("->")
        src = tkns[:i]
        dsts = parse_dsts(tkns[i+1:])
        return Cmd(assign_method, [src, dsts])
    elif is_move_args:
        args = parse_legacy_assign_args(tkns)
        src = args[0]
        dsts = args[1:]
        return Cmd(assign_method, [src, dsts])

    return Cmd("error", [tkns])

def parse_legacy_assign_args(tkns: list[str]) -> list[str]:
    args = []
    if "," in tkns:
        i = tkns.index(",")
        arg = parse_val(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    args.extend(parse_dsts(tkns))
    return args
def parse_args(tkns: list[str]) -> list[str]:
    args = []
    while "," in tkns:
        i = tkns.index(",")
        arg = parse_val(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    arg = parse_val(tkns)
    args.append(arg)

    return args
def parse_dsts(tkns: list[str]) -> list[str]:
    args = []
    while "," in tkns:
        i = tkns.index(",")
        arg = parse_lval(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    arg = parse_lval(tkns)
    args.append(arg)

    return args

def parse_lval(tkns: list[str]) -> Node:
    if len(tkns) > 1:
        if tkns[-1] in ["+", "-"]:
            return Node("annotated", [tkns[-1], parse_val(tkns[:-1])])
    return parse_val(tkns)
def parse_val(tkns: list[str]) -> Node:
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

def parse_var_decls(tkns: list[str]) -> list[str]:
    args = []
    while "," in tkns:
        i = tkns.index(",")
        arg = parse_var_decl(tkns[:i])
        args.append(arg)
        tkns = tkns[i+1:]

    arg = parse_var_decl(tkns)
    args.append(arg)

    return args
def parse_var_decl(tkns: list[str]) -> Node:
    if len(tkns) >= 1:
        if tkns[0].isidentifier():
            name = tkns[0]
            if len(tkns) > 2 and tkns[1] == ":":
                typ = parse_type(tkns[2:])
            else:
                typ = Node("type", [Node("primitive", [config["default_type"]])])
            return Node("var_decl", [name, typ])

    return Node("error", tkns)

def find_right_recur_opr(tkns: list[str], oprs: list[str]) -> tuple[str, int]:
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

def find_left_recur_opr(tkns: list[str], oprs: list[str]) -> tuple[str, int]:
    indices = []
    for opr in oprs:
        try:
            idx = list_last_index(tkns, opr)
        except:
            idx = -1
        indices.append(idx)

    max_idx = max(*indices)
    if max_idx == -1:
        return "", -1

    opr_idx = indices.index(max_idx)
    return oprs[opr_idx], max_idx

def parse_const_expr(tkns: list[str]) -> Node:
    return parse_const_add(tkns)
def parse_const_add(tkns: list[str]) -> Node:
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
def parse_const_mul(tkns: list[str]) -> Node:
    if len(tkns) >= 3:
        opr, idx = find_left_recur_opr(tkns, ["+", "/", "%"])
        if idx != -1:
            left = parse_const_mul(tkns[:idx])
            right = parse_const_val(tkns[idx + 1:])
            if opr == "*":
                return Node("mul", [left, right])
            elif opr == "/":
                return Node("div", [left, right])
            elif opr == "%":
                return Node("mod", [left, right])

    return parse_const_val(tkns)
def parse_const_val(tkns: list[str]) -> Node:
    if len(tkns) == 1:
        if tkns[0].isidentifier():
            return Node("id", [tkns[0]])
        elif tkns[0].isnumeric():
            return Node("num", [tkns[0]])
        elif tkns[0].startswith('"') and tkns[0].endswith('"'):
            return Node("str", [tkns[0][1: -1]])

    return Node("error", tkns)

def parse_type(tkns: list[str]) -> Node:
    if len(tkns) >= 1:
        if len(tkns) >= 3 and ("[" in tkns) and tkns[-1] == "]":
            indexter_start = list_last_index(tkns, "[")
            array_len = parse_const_expr(tkns[indexter_start + 1:-1])
            if indexter_start == 0:
                elm_type = Node("primitive", [config["default_type"]])
            else:
                elm_type = parse_type(tkns[:indexter_start])
            return Node("array", [array_len, elm_type])
        if tkns[0].isidentifier():
            name = tkns[0]
            return Node("primitive", [name])

    return Node("error", tkns)



try:
    while True:
        cmd = parse_line(input(">"))
        if cmd.op != "empty":
            print(cmd)
except Exception as e:
    # raise e
    pass
