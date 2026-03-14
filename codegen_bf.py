from typing import cast, Tuple
from c_config import *
from bfhla_struct import *
import re

re_raw_var = re.compile(r"^([a-zA-Z$_][a-zA-Z0-9$_]*)(?:\[([+\\-]|)(\d+)\]|)")


def print_indented(i: int, s: str):
    print(codegen.indent_unit * i + s)

def get_var_info(src: str, current_addr: int, scopes: list[dict] = None) -> Tuple[bool, bool, int]:
    """result: (is_var, is_relative, addr)"""

    name = src
    if "[" in name:
        name = name[:name.index("[")]
    src_is_var = name.isidentifier() or name == "$"
    if not src_is_var:
        n = -1
        is_rel = False
        return (src_is_var, is_rel, n)

    m = re_raw_var.match(src)
    if m:
        base = m.group(1)
        sign = m.group(2)
        offset = m.group(3)

        if sign is None:
            sign = ""
        no_idx = offset is None
        if no_idx:
            offset = 0
        else:
            offset = int(offset)

        if base == "$":
            offset = -offset if sign == "-" else offset
            if current_addr != -1:
                offset += current_addr

            return True, True, offset
        elif scopes is not None:
            for scope in reversed(scopes):
                scope_addr = scope["base"] + scope["offset"]
                addr = -1
                for i, v in enumerate(scope["vars"]):
                    if base == v:
                        addr = scope_addr + i

                if base == scope["name"]:
                    addr = scope_addr

                if addr != -1:
                    if sign == "-":
                        addr -= offset
                    else:
                        addr += offset
                    return True, False, addr
        else:
            print("scopes is None")

        raise ValueError(f"Variable '{base}' not found in any scope")
    else:
        print(f"failed to parse '{src}'")

    raise ValueError(f"Invalid selector '{src}'")


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
                "vars": scope.var_names()
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
                src_is_var, is_rel, offset = get_var_info(sel.to_bfhla(), current_addr, scopes)
                s = bf_selector(current_addr, offset)
                current_addr = offset
                print_indented(blks, f"{s}  # at {current_addr}")

        elif op == "config":
            pass
        elif op in ["move", "copy"]:
            assign_pair = cast(AssignArgs, args)
            src_is_var, is_rel, offset = get_var_info(assign_pair.src.to_bfhla(), current_addr, scopes)
            src_addr = offset

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
                        src_is_var, is_rel, offset = get_var_info(dst.addr(), current_addr, scopes)

                        s += bf_selector(tmp_addr, offset)
                        s += "[-]"
                        tmp_addr = offset

                    s += bf_selector(tmp_addr, tmp_addr0)
                    tmp_addr = tmp_addr0

                s += "["

                for dst in assign_pair.dsts:
                    src_is_var, is_rel, offset = get_var_info(dst.addr(), current_addr, scopes)

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
                    src_is_var, is_rel, offset = get_var_info(dst.addr(), current_addr, scopes)

                    s += bf_selector(tmp_addr, offset)
                    tmp_addr = offset

                    if dst.has_clear():
                        s += "[-]"
                    s += ("+" if dst.multiplier >= 0 else "-") * abs(dst.multiplier) * src_num

                if current_addr != -1:
                    s += bf_selector(tmp_addr, current_addr)

                print_indented(blks, f"{s}  # const")

            if op == "copy" and src_is_var:
                print_indented(blks, f"# restore copy at here")
                # print_indented(blks, f"{src_addr} = 0;")
        elif op in ["clear", "input", "print"]:
            addrs = cast(AddrSelectorArgs, args)
            tmp_addr = current_addr if current_addr != -1 else 0
            tmp_addr0 = tmp_addr
            s = ""
            f = {
                "clear": "[-]",
                "input": ",",
                "print": ".",
            }[op]
            for addr in addrs.addrs:
                src_is_var, is_rel, offset = get_var_info(addr.to_bfhla(), current_addr, scopes)

                s += bf_selector(tmp_addr, offset)
                s += f
                tmp_addr = offset
            s += bf_selector(tmp_addr, tmp_addr0)
            print_indented(blks, f"{s}  # {op}")
        elif op == "skipr":
            addrs = cast(AddrSelectorArgs, args)
            n = int(addrs.addrs[0])
            if current_addr != -1:
                print_indented(blks, bf_selector(0, current_addr))
                current_addr = -1
            print_indented(blks, f"[{'>' * n}]")
        elif op == "skipl":
            addrs = cast(AddrSelectorArgs, args)
            n = int(addrs.addrs[0])
            if current_addr != -1:
                print_indented(blks, bf_selector(0, current_addr))
                current_addr = -1
            print_indented(blks, f"[{'<' * n}]")
        elif op == "bf":
            src = cast(BfArgs, args).bf
            s = ""
            for bf_op, bf_arg in src:
                if bf_op == "+":
                    s += "+" * bf_arg
                elif bf_op == "-":
                    s += "-" * bf_arg
                elif bf_op == ">":
                    if current_addr != -1:
                        current_addr += bf_arg
                    s += ">" * bf_arg
                elif bf_op == "<":
                    if current_addr != -1:
                        if current_addr - bf_arg < 0:
                            s += bf_selector(0, current_addr)
                            current_addr = -1
                        else:
                            current_addr -= 1
                    s += "<" * bf_arg
                elif bf_op == ",":
                    s += ","
                elif bf_op == ".":
                    s += "."
                elif bf_op == "0":
                    s += "[-]"
                elif bf_op == "[":
                    if current_addr != -1:
                        s += bf_selector(0, current_addr)
                        current_addr = -1
                    s += "["
                    blks += 1
                    blk_defers.append((-1, ""))
                elif bf_op == "]":
                    blks -= 1
                    blk_defers.pop()
                    s += "]"
            print_indented(blks, f"{s}  # inline bf")
        elif op == "balanced_loop_at":
            addrs = cast(AddrSelectorArgs, args)
            src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            s = bf_selector(current_addr, offset)
            current_addr = offset
            blk_defers.append((current_addr, ""))

            print_indented(blks, f"{s}[  # balanced at var")
            blks += 1
        elif op == "ifnz":
            addrs = cast(AddrSelectorArgs, args)
            src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            s = bf_selector(current_addr, offset)
            current_addr = offset
            blk_defers.append((current_addr, "[-]"))

            print_indented(blks, f"{s}[  # if")
            blks += 1
        elif op == "predec_for":
            addrs = cast(AddrSelectorArgs, args)
            src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            s = bf_selector(current_addr, offset)
            current_addr = offset
            blk_defers.append((current_addr, ""))

            print_indented(blks, f"{s}[-  # for")
            blks += 1
        elif op == "postdec_for":
            addrs = cast(AddrSelectorArgs, args)
            src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            s = bf_selector(current_addr, offset)
            current_addr = offset
            blk_defers.append((current_addr, "-"))

            print_indented(blks, f"{s}[  # for")
            blks += 1
        elif op == "balanced_loop":
            if current_addr != -1:
                print_indented(blks, bf_selector(0, current_addr))
                current_addr = -1
            print_indented(blks, "[  # balanced")
            blks += 1
            blk_defers.append((current_addr, ""))
        elif op == "loop":
            if current_addr != -1:
                print_indented(blks, bf_selector(0, current_addr))
                current_addr = -1
            print_indented(blks, "[")
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
