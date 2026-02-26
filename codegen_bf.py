from typing import cast, Tuple
from c_config import *
from bfhla_struct import *
import re

re_raw_var = re.compile(r"^([a-zA-Z$_][a-zA-Z0-9$_]*)\[(|[+\\-])(\d+)\]$")
re_bfrle_step = re.compile(r"^(.{1})(\d*)(|.*)$")

def print_indented(i: int, s: str):
    print(codegen.indent_unit * i + s)

def addr_from_var(var: str, scopes: list[dict] = None) -> Tuple[str, bool, int]:
    """result: (var_repr, is_relative, addr)"""
    m = re_raw_var.match(var)
    if m:
        base = m.group(1)
        sign = m.group(2)
        offset = int(m.group(3))

        if base == "$":
            return f"p[{sign}{offset}]", True, offset
        elif scopes is not None:
            for scope in reversed(scopes):
                if base == scope["name"]:
                    addr = scope["base"] + scope["offset"];
                    if sign == "-":
                        addr -= offset
                    else:
                        addr += offset
                    return f"{scope['name']}[{addr}]", False, addr

        raise ValueError(f"Variable '{var}' not found in any scope")

    for scope in reversed(scopes):
        if var in scope["vars"]:
            offset = scope["vars"].index(var)
            addr = scope["base"] + scope["offset"] + offset
            return f"{scope['name']}[{addr}]", False, addr

    raise ValueError(f"Variable '{var}' not found in any scope")

def sanitize(s: str, scopes: list[dict] = None) -> Tuple[bool, str, bool, int]:
    addr = s
    if "[" in addr:
        addr = addr[:addr.index("[")]
    src_is_var = addr.isidentifier() or addr == "$"
    if src_is_var:
        addr, is_rel, n = addr_from_var(s, scopes)
    else:
        n = -1
        is_rel = False
    return (src_is_var, addr, is_rel, n)

def bf_selector(_from: int, _to: int) -> str:
    return "<" * (_from - _to) if _from > _to else ">" * (_to - _from)


def print_bf(code: list[IrStep]):
    blks = 0
    blk_defers = []
    current_addr: int = 0
    scopes = []

    for step in code:
        op, args = step.get_pair()
        if op == "scope":
            scope = cast(ScopeDeclArgs, args)
            size = int(scope.size)
            base = int(scope.base)
            offset = int(scope.offset)

            scope = {
                "name": scope.name,
                "size": size,
                "base": base,
                "offset": offset,
                "vars": scope.vars
            }
            scopes.append(scope)
        elif op == "at":
            addrs = cast(AddrSelectorArgs, args)
            sel = cast(Expr, addrs.addrs[0])
            if sel.op == "signed":
                sel2 = cast(Expr, sel.args[1])
                n = int(sel2)
                if sel.args[0] == "-":
                    n = -n

                s = bf_selector(0, n)
                if current_addr == -1:
                    print_indented(blks, f"{s}")
                else:
                    current_addr += n
                    print_indented(blks, f"{s}  # at {current_addr}")
            elif current_addr == -1:
                print_indented(blks, f"error  unable to access to fixed address  # at unknown")
            else:
                src_is_var, src_addr, is_rel, offset = sanitize(sel.to_bfhla(), scopes)
                s = bf_selector(current_addr, offset)
                current_addr = offset
                print_indented(blks, f"{s}  # at {current_addr}")

        elif op == "config":
            pass
        elif op in ["move", "copy"]:
            assign_pair = cast(AssignArgs, args)
            src_is_var, src_addr, is_rel, offset = sanitize(assign_pair.src.to_bfhla(), scopes)

            if src_is_var:
                tmp_addr = offset
                tmp_addr0 = tmp_addr
                if current_addr != -1:
                    s = bf_selector(current_addr, tmp_addr)
                else:
                    s = ""

                if any(map(LValue.has_clear, assign_pair.dsts)):
                    for dst in assign_pair.dsts:
                        if not dst.clear:
                            continue
                        addr, is_rel, offset = addr_from_var(dst.addr(), scopes)
                        if is_rel and current_addr != -1:
                            offset += current_addr

                        s += bf_selector(tmp_addr, offset)
                        s += "[-]"
                        tmp_addr = offset

                    s += bf_selector(tmp_addr, tmp_addr0)
                    tmp_addr = tmp_addr0

                s += "["

                for dst in assign_pair.dsts:
                    addr, is_rel, offset = addr_from_var(dst.addr(), scopes)
                    if is_rel and current_addr != -1:
                        offset += current_addr

                    s += bf_selector(tmp_addr, offset)
                    s += ("+" if dst.multiplier >= 0 else "-") * abs(dst.multiplier)

                    tmp_addr = offset

                s += bf_selector(tmp_addr, tmp_addr0)
                tmp_addr = tmp_addr0
                s += "-]"

                if current_addr != -1:
                    s += bf_selector(tmp_addr, current_addr)

                print_indented(blks, f"{s}  # move")
            else:
                src_num = int(assign_pair.src)
                if current_addr != -1:
                    tmp_addr = current_addr
                else:
                    tmp_addr = 0

                s = ""
                for dst in assign_pair.dsts:
                    addr, is_rel, offset = addr_from_var(dst.addr(), scopes)
                    if is_rel and current_addr != -1:
                        offset += current_addr

                    s += bf_selector(tmp_addr, offset)
                    tmp_addr = offset

                    if dst.has_clear():
                        s += "[-]"
                    s += ("+" if dst.multiplier >= 0 else "-") * abs(dst.multiplier) * src_num

                if current_addr != -1:
                    s += bf_selector(tmp_addr, current_addr)

                print_indented(blks, f"{s}  # const")

            # if op == "copy" and src_is_var:
            #     print_indented(blks, f"{src_addr} = 0;")
        elif op in ["clear", "input", "print"]:
            addrs = cast(AddrSelectorArgs, args)
            tmp_addr = current_addr
            s = ""
            f = {
                "clear": "[-]",
                "input": ",",
                "print": ".",
            }[op]
            for addr in addrs.addrs:
                addr, is_rel, offset = addr_from_var(addr.to_bfhla(), scopes)
                if is_rel:
                    offset += current_addr
                s += bf_selector(tmp_addr, offset)
                s += f
                tmp_addr = offset
            s += bf_selector(tmp_addr, current_addr)
            print_indented(blks, f"{s}  # {op}")
        elif op == "skipr":
            addrs = cast(AddrSelectorArgs, args)
            n = int(addrs.addrs[0])
            print_indented(blks, f"[{'>' * n}]")
            current_addr = -1
        elif op == "skipl":
            addrs = cast(AddrSelectorArgs, args)
            n = int(addrs.addrs[0])
            print_indented(blks, f"[{'<' * n}]")
            current_addr = -1
        elif op == "bf":
            inline_bf = cast(BfArgs, args)
            src = inline_bf.text
            s = ""
            while len(src):
                m = re_bfrle_step.match(src)
                if not m:
                    break
                c, n, src = m.groups()
                if n == "":
                    n = 1
                else:
                    n = int(n)

                if c == "+":
                    s += "+" * n
                elif c == "-":
                    s += "-" * n
                elif c == ">":
                    s += ">" * n
                    current_addr += n
                elif c == "<":
                    s += "<" * n
                    current_addr -= n
                elif c == ",":
                    s += ","
                elif c == ",":
                    s += "."
                elif c == "[":
                    s += "["
                    current_addr = -1
                    blks += 1
                    blk_defers.append("")
                elif c == "]":
                    current_addr = -1
                    blks -= 1
                    blk_defers.pop()
                    s += "]"
            print_indented(blks, f"{s}  # inline bf")
        elif op == "balanced_loop_at":
            addrs = cast(AddrSelectorArgs, args)
            addr = addrs.to_bfhla()
            _, addr, is_rel, offset = sanitize(addr, scopes)
            if is_rel:
                offset += current_addr
            s = bf_selector(current_addr, offset)
            current_addr = offset
            blk_defers.append((current_addr, ""))

            print_indented(blks, f"{s}[  # balanced")
            blks += 1
        elif op == "ifnz":
            addrs = cast(AddrSelectorArgs, args)
            addr = addrs.to_bfhla()
            _, addr, is_rel, offset = sanitize(addr, scopes)
            if is_rel:
                offset += current_addr
            s = bf_selector(current_addr, offset)
            current_addr = offset
            blk_defers.append((current_addr, "[-]"))

            print_indented(blks, f"{s}[  # if")
            blks += 1
        elif op == "predec_for":
            addrs = cast(AddrSelectorArgs, args)
            addr = addrs.to_bfhla()
            _, addr, is_rel, offset = sanitize(addr, scopes)
            if is_rel:
                offset += current_addr
            s = bf_selector(current_addr, offset)
            current_addr = offset
            blk_defers.append((current_addr, ""))

            print_indented(blks, f"{s}[-  # for")
            blks += 1
        elif op == "postdec_for":
            addrs = cast(AddrSelectorArgs, args)
            addr = addrs.to_bfhla()
            _, addr, is_rel, offset = sanitize(addr, scopes)
            if is_rel:
                offset += current_addr
            s = bf_selector(current_addr, offset)
            current_addr = offset
            blk_defers.append((current_addr, "-"))

            print_indented(blks, f"{s}[  # for")
            blks += 1
        elif op == "balanced_loop":
            print_indented(blks, "[  # balanced")
            blks += 1
            blk_defers.append((current_addr, ""))
        elif op == "loop":
            print_indented(blks, "[")
            current_addr = -1
            blks += 1
            blk_defers.append((-1, ""))
        elif op == "end":
            loop_addr, s = blk_defers.pop()
            if loop_addr != -1:
                s = bf_selector(current_addr, loop_addr) + s
                current_addr = loop_addr
            blks -= 1
            s += "]"
            print_indented(blks, s)
        elif op == "comment":
            raw = cast(RawArgs, args)
            print_indented(blks, raw.args["text"])
        elif op == "error":
            raw = cast(RawArgs, args)
            print_indented(blks, f"error {raw.args['src']}")
        else:
            print_indented(blks, f"# unknown instruction: {op}")

    print_indented(blks, "# end")
