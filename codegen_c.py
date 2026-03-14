from typing import cast, Tuple
from c_config import *
from bfhla_struct import *
import re

re_raw_var = re.compile(r"^([0-9]+|[a-zA-Z$_][a-zA-Z0-9$_]*)(?:\[([+\\-]|)(\d+)\]|)")


def print_indented(i: int, s: str):
    print(codegen.indent_unit * i + s)

def get_var_info(src: str, current_addr: int, scopes: list[dict] = None) -> Tuple[str, bool, bool, int]:
    """result: (var_repr, is_var, is_relative, addr)"""

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

        if base.isdigit():
            return base, False, False, offset
        elif base == "$":
            offset = -offset if sign == "-" else offset
            if current_addr != -1:
                offset += current_addr

            return f"p[{offset}]",True, True, offset
        elif scopes is not None:
            for scope in reversed(scopes):
                scope_addr = scope["base"] + scope["offset"]
                addr = -1
                for i, v in enumerate(scope["vars"]):
                    if base == v:
                        addr = scope_addr + i
                        return f"{scope['name']}[{i}]", True, False, addr

                if base == scope["name"]:
                    addr = scope_addr

                if addr != -1:
                    if sign == "-":
                        addr -= offset
                    else:
                        addr += offset
                    return f"{scope['name']}[{offset}]", True, False, addr
        else:
            print("scopes is None")

        raise ValueError(f"Variable '{base}' not found in any scope")
    else:
        print(f"failed to parse '{src}'")

    raise ValueError(f"Invalid selector '{src}'")

def print_c(code: list[IrStep]):
    blks = 0
    blk_defers = []
    current_addr = 0
    scopes = []

    print_indented(blks, "#include <stdio.h>")
    print_indented(blks, "#include <stdint.h>")
    print_indented(blks, f"{codegen.cell_type} {codegen.buf_name}[{codegen.buf_size}];")
    print_indented(blks, "int main() {")
    print_indented(blks, f"{codegen.cell_type} *p = {codegen.buf_name};")

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
            print_indented(blks, f"{codegen.cell_type} *{scope['name']} = {codegen.buf_name} + {base + offset};")
        elif op == "at":
            addrs = cast(AddrSelectorArgs, args)
            sel = cast(Expr, addrs.addrs[0])
            if sel.op == "signed":
                sel2 = cast(Expr, sel.args[1])
                n = int(sel2)
                if sel.args[0] == "-":
                    n = -n

                if current_addr != -1:
                    current_addr += n

                if current_addr == -1:
                    print_indented(blks, f"p {sel.args[0]}= {sel.args[1].to_bfhla()};")
            else:
                addr, src_is_var, is_rel, offset = get_var_info(sel.to_bfhla(), current_addr, scopes)

                current_addr = offset
                # print_indented(blks, f"p = {codegen.buf_name} + {offset};")

        elif op == "config":
            pass
        elif op in ["move", "copy"]:
            assign_pair = cast(AssignArgs, args)
            src_addr, src_is_var0, is_rel, offset = get_var_info(assign_pair.src.to_bfhla(), current_addr, scopes)

            for dst in assign_pair.dsts:
                addr, src_is_var, is_rel, offset = get_var_info(dst.addr(), current_addr, scopes)

                s = str(addr)
                s += (" = " if dst.clear
                      else " += " if dst.multiplier >= 0
                      else " -= ")
                if abs(dst.multiplier) > 1:
                    s += f"{src_addr} * {abs(dst.multiplier)};"
                else:
                    s += f"{src_addr};"

                print_indented(blks, s)
            if op != "copy" and src_is_var0:
                print_indented(blks, f"{src_addr} = 0;")
        elif op == "clear":
            addrs = cast(AddrSelectorArgs, args)
            for addr in addrs.addrs:
                addr, src_is_var, is_rel, offset = get_var_info(addr.to_bfhla(), current_addr, scopes)
                print_indented(blks, f"{addr} = 0;")
        elif op == "input":
            addrs = cast(AddrSelectorArgs, args)
            addr, src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)
            print_indented(blks, f"{addr} = getchar();")
        elif op == "print":
            addrs = cast(AddrSelectorArgs, args)
            addr, src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)
            print_indented(blks, f"putchar({addr});")
        elif op == "skipr":
            addrs = cast(AddrSelectorArgs, args)
            if current_addr != -1:
                print_indented(blks, f"p = &mem[{current_addr}];")
                current_addr = -1
            print_indented(blks, f"while (*p) p += {addrs.to_bfhla()};")
        elif op == "skipl":
            addrs = cast(AddrSelectorArgs, args)
            if current_addr != -1:
                print_indented(blks, f"p = &mem[{current_addr}];")
                current_addr = -1
            print_indented(blks, f"while (*p) p -= {addrs.to_bfhla()};")
        elif op == "bf":
            src = cast(BfArgs, args).bf

            for bf_op, bf_arg in src:
                if bf_op == "+":
                    if current_addr != -1:
                        print_indented(blks, f"bf_mem[{current_addr}] += {bf_arg};")
                    else:
                        print_indented(blks, f"*p += {bf_arg};")
                elif bf_op == "-":
                    if current_addr != -1:
                        print_indented(blks, f"bf_mem[{current_addr}] -= {bf_arg};")
                    else:
                        print_indented(blks, f"*p -= {bf_arg};")
                elif bf_op == ">":
                    if current_addr != -1:
                        current_addr += bf_arg
                    else:
                        print_indented(blks, f"p += {bf_arg};")
                elif bf_op == "<":
                    if current_addr != -1:
                        if current_addr - bf_arg < 0:
                            print_indented(blks, f"p = bf_mem + {current_addr};")
                            current_addr = -1
                        else:
                            current_addr -= 1
                    if current_addr == -1:
                        print_indented(blks, f"p -= {bf_arg};")
                elif bf_op == ",":
                    if current_addr != -1:
                        print_indented(blks, f"bf_mem[{current_addr}] = getchar();")
                    else:
                        print_indented(blks, f"*p = getchar();")
                elif bf_op == ".":
                    if current_addr != -1:
                        print_indented(blks, f"putchar(bf_mem[{current_addr}]);")
                    else:
                        print_indented(blks, f"putchar(*p);")
                elif bf_op == "0":
                    if current_addr != -1:
                        print_indented(blks, f"bf_mem[{current_addr}] = 0;")
                    else:
                        print_indented(blks, f"*p = 0;")
                elif bf_op == "[":
                    if current_addr != -1:
                        print_indented(blks, f"p = bf_mem + {current_addr};")
                        current_addr = -1
                    print_indented(blks, "while (*p) {")
                    blks += 1
                    blk_defers.append((current_addr, ""))
                elif bf_op == "]":
                    blks -= 1
                    blk_defers.pop()
                    print_indented(blks, "}")
        elif op == "balanced_loop_at":
            addrs = cast(AddrSelectorArgs, args)
            addr, src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            current_addr = offset
            blk_defers.append((current_addr, ""))

            print_indented(blks, f"while ({addr}) {{")
            blks += 1
        elif op == "ifnz":
            addrs = cast(AddrSelectorArgs, args)
            addr, src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            current_addr = offset
            blk_defers.append((current_addr, f"{addr} = 0;"))

            print_indented(blks, f"if ({addr}) {{")
            blks += 1
        elif op == "predec_for":
            addrs = cast(AddrSelectorArgs, args)
            addr, src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            current_addr = offset
            blk_defers.append((current_addr, ""))

            print_indented(blks, f"for (; {addr}; --{addr}) {{")
            blks += 1
        elif op == "postdec_for":
            addrs = cast(AddrSelectorArgs, args)
            addr, src_is_var, is_rel, offset = get_var_info(addrs.to_bfhla(), current_addr, scopes)

            current_addr = offset
            blk_defers.append((current_addr, f"--{addr};"))

            print_indented(blks, f"while ({addr}) {{")
            blks += 1
        elif op == "balanced_loop":
            if current_addr != -1:
                print_indented(blks, f"p = bf_mem + {current_addr};")
                current_addr = -1
            print_indented(blks, "while (p[0]) {")
            blks += 1
            blk_defers.append((current_addr, ""))
        elif op == "loop":
            if current_addr != -1:
                print_indented(blks, f"p = bf_mem + {current_addr};")
                current_addr = -1
            print_indented(blks, "while (*p) {")
            blks += 1
            blk_defers.append((current_addr, ""))
        elif op == "end":
            loop_addr, s = blk_defers.pop()
            if loop_addr != -1:
                current_addr = loop_addr
            if s != "":
                print_indented(blks, s)
            blks -= 1
            print_indented(blks, "}")
        elif op == "comment":
            raw = cast(RawArgs, args)
            print_indented(blks, raw.args["text"])
        elif op == "error":
            raw = cast(RawArgs, args)
            print_indented(blks, f"error {raw.args['src']}")
        else:
            print_indented(blks, f"# unknown instruction: {op}")

    print_indented(blks, "return 0; } /* end main */")
