from typing import cast, Tuple, Optional
import config.c as c_config
from bfhla.struct import *
import re


def print_indented(i: int, s: str):
    print(c_config.codegen.indent_unit * i + s)


def get_var_info(src: str, current_addr: int, scopes: Optional[list[dict]] = None) -> Tuple[bool, bool, int]:
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


def bf_selector(_from: int, _to: int) -> list[str]:
    s = "RIGHT" if _from < _to else "LEFT"

    return [f"MOV {s}, P"] * abs(_from - _to)


def bfir_to_assemblerfuck(code: list[IrStep]) -> list[str]:
    blks = 0
    blk_defers = []
    current_addr: int = 0
    scopes = []
    result = []

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

                result.extend(bf_selector(0, n))

                if current_addr != -1:
                    current_addr += n
            elif current_addr == -1:
                result.append(f"error  unable to access to fixed address  # at unknown")
            else:
                src_is_var, is_rel, offset = get_var_info(sel.to_bfhla(), current_addr, scopes)
                result.extend(bf_selector(current_addr, offset))

                current_addr = offset
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
                    result.extend(bf_selector(current_addr, tmp_addr))
    
                if any(map(LValue.has_clear, assign_pair.dsts)):
                    for dst in assign_pair.dsts:
                        if not dst.clear:
                            continue
                        src_is_var, is_rel, offset = get_var_info(dst.addr(), current_addr, scopes)

                        result.extend(bf_selector(tmp_addr, offset))
                        result.append("SET 0")
                        tmp_addr = offset

                    result.extend(bf_selector(tmp_addr, tmp_addr0))
                    tmp_addr = tmp_addr0

                result.append("UNTIL 0")

                for dst in assign_pair.dsts:
                    src_is_var, is_rel, offset = get_var_info(dst.addr(), current_addr, scopes)

                    result.extend(bf_selector(tmp_addr, offset))

                    s = ("INC " if dst.multiplier >= 0 else "DEC ") + str(abs(dst.multiplier))
                    result.append(s)

                    tmp_addr = offset

                result.extend(bf_selector(tmp_addr, tmp_addr0))
                tmp_addr = tmp_addr0

                result.append("DEC 1")
                result.append("END")

                if current_addr != -1:
                    result.extend(bf_selector(tmp_addr, current_addr))
            else:
                src_num = int(assign_pair.src)
                if current_addr != -1:
                    tmp_addr = current_addr
                else:
                    tmp_addr = 0

                s = ""
                for dst in assign_pair.dsts:
                    src_is_var, is_rel, offset = get_var_info(dst.addr(), current_addr, scopes)

                    result.extend(bf_selector(tmp_addr, offset))
                    tmp_addr = offset

                    if dst.has_clear() and dst.multiplier > 0:
                        result.append(f"SET {dst.multiplier}")
                    else:
                        if dst.has_clear():
                            result.append("SET 0")

                        s = ("INC " if dst.multiplier >= 0 else "DEC ") + str(abs(dst.multiplier))
                        result.append(s)

                if current_addr != -1:
                    result.extend(bf_selector(tmp_addr, current_addr))

            if op == "copy" and src_is_var:
                result.append(f"# restore copy at here")
                # result.append(f"{src_addr} = 0;")
        elif op in ["clear", "input", "print"]:
            addrs = cast(AddrSelectorArgs, args)
            tmp_addr = current_addr
            s = ""
            f = {
                "clear": "SET 0",
                "input": "MOV P, IN",
                "print": "MOV P, OUT",
            }[op]
            for addr in addrs.addrs:
                src_is_var, is_rel, offset = get_var_info(addr.to_bfhla(), current_addr, scopes)

                result.extend(bf_selector(tmp_addr, offset))
                result.append(f)
                tmp_addr = offset

            result.extend(bf_selector(tmp_addr, current_addr))
            # .. done (codegen_bf->_assemblerfuck)
        elif op == "skipr":
            addrs = cast(AddrSelectorArgs, args)
            n = int(addrs.addrs[0])
            if current_addr != -1:
                result.extend(bf_selector(0, current_addr))
                current_addr = -1
            result.append("UNTIL 0")
            result.extend(["MOV RIGHT, P"] * n)
            result.append("END")
        elif op == "skipl":
            addrs = cast(AddrSelectorArgs, args)
            n = int(addrs.addrs[0])
            if current_addr != -1:
                result.extend(bf_selector(0, current_addr))
                current_addr = -1
            result.append("UNTIL 0")
            result.extend(["MOV LEFT, P"] * n)
            result.append("END")
        elif op == "bf":
            inline_bf = cast(BfArgs, args)
            src = inline_bf.bf
            for bf_op, bf_arg in src:
                if bf_op == "+":
                    result.append(f"ADD {bf_arg}")
                elif bf_op == "-":
                    result.append(f"SUB {bf_arg}")
                elif bf_op == ">":
                    if current_addr != -1:
                        current_addr += bf_arg
                    
                    result.extend(["MOV RIGHT, P"] * bf_arg)
                elif bf_op == "<":
                    if current_addr != -1:
                        if current_addr - bf_arg < 0:
                            result.extend(bf_selector(0, current_addr))
                            current_addr = -1
                        else:
                            current_addr -= 1

                    result.extend(["MOV LEFT, P"] * bf_arg)
                elif bf_op == ",":
                    result.append("MOV P, IN")
                elif bf_op == ".":
                    result.append("MOV P, OUT")
                elif bf_op == "[":
                    if current_addr != -1:
                        result.extend(bf_selector(0, current_addr))
                        current_addr = -1

                    result.append("UNTIL 0")
                    blks += 1
                    blk_defers.append((-1, []))
                elif bf_op == "]":

                    blks -= 1
                    blk_defers.pop()
                    result.append("END")
        elif op == "balanced_loop_at":
            addrs = cast(AddrSelectorArgs, args)
            src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            result.extend(bf_selector(current_addr, offset))
            current_addr = offset
            blk_defers.append((current_addr, []))

            result.append("UNTIL 0")
            blks += 1
        elif op == "ifnz":
            addrs = cast(AddrSelectorArgs, args)
            src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            result.extend(bf_selector(current_addr, offset))
            current_addr = offset
            blk_defers.append((current_addr, ["SET 0"]))

            result.append("UNTIL 0")
            blks += 1
        elif op == "predec_for":
            addrs = cast(AddrSelectorArgs, args)
            src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            result.extend(bf_selector(current_addr, offset))
            current_addr = offset
            blk_defers.append((current_addr, []))

            result.append("UNTIL 0")
            blks += 1
            result.append("DEC 1")
        elif op == "postdec_for":
            addrs = cast(AddrSelectorArgs, args)
            src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            result.extend(bf_selector(current_addr, offset))
            current_addr = offset
            blk_defers.append((current_addr, ["DEC 1"]))

            result.append("UNTIL 0")
            blks += 1
        elif op == "balanced_loop":
            if current_addr != -1:
                result.extend(bf_selector(0, current_addr))
                current_addr = -1

            result.append("UNTIL 0")
            blks += 1
            blk_defers.append((current_addr, []))
        elif op == "loop":
            if current_addr != -1:
                result.extend(bf_selector(0, current_addr))
                current_addr = -1

            result.append("UNTIL 0")
            blks += 1
            blk_defers.append((-1, []))
        elif op == "end":
            loop_addr, ss = blk_defers.pop()
            if loop_addr != -1:
                result.extend(bf_selector(current_addr, loop_addr))
                current_addr = loop_addr

            result.extend(ss)
            blks -= 1
            result.append("END")
        elif op == "comment":
            raw = cast(RawArgs, args)
            result.append(raw.args["text"])
        elif op == "error":
            raw = cast(RawArgs, args)
            result.append(f"# error {raw.args['src']}")
        else:
            result.append(f"# unknown instruction: {op}")

    return result


def assemblerfuck_optimize(code: list[str]):
    i = 0
    while i + 1 < len(code):
        if set((code[i], code[i + 1])) == set(("MOV LEFT, P", "MOV RIGHT, P")):
            code.pop(i)
            code.pop(i)
            if i > 0:
                i -= 1

            continue

        i += 1


def print_assemblerfuck(code: list[IrStep]):
    asm = bfir_to_assemblerfuck(code)
    assemblerfuck_optimize(asm)
    i = 0
    for s in asm:
        if s == "END":
            i -= 1

        print_indented(i, s)

        if s == "UNTIL 0":
            i += 1
