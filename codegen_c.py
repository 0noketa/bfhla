from typing import cast, Tuple
from c_config import *
from bfhla_struct import *
import re

re_raw_var = re.compile(r"^([a-zA-Z$_][a-zA-Z0-9$_]*)\[(|[+\\-])(\d+)\]$")
re_bfrle_step = re.compile(r"^(.{1})(\d*)(|.*)$")

def print_indented(i: int, s: str):
    print(codegen.indent_unit * i + s)

def addr_from_var(var: str, scopes: list[dict] = None) -> Tuple[str, int]:
    m = re_raw_var.match(var)
    if m:
        base = m.group(1)
        sign = m.group(2)
        offset = int(m.group(3))

        if base == "$":
            return f"p[{sign}{offset}]", -1
        elif scopes is not None:
            for scope in reversed(scopes):
                if base == scope["name"]:
                    addr = scope["base"] + scope["offset"];
                    if sign == "-":
                        addr -= offset
                    else:
                        addr += offset
                    return f"{scope['name']}[{addr}]", addr

        raise ValueError(f"Variable '{var}' not found in any scope")

    for scope in reversed(scopes):
        if var in scope["vars"]:
            offset = scope["vars"].index(var)
            addr = scope["base"] + scope["offset"] + offset
            return f"{scope['name']}[{addr}]", addr

    raise ValueError(f"Variable '{var}' not found in any scope")

def sanitize(s: str, scopes: list[dict] = None) -> Tuple[bool, str, int]:
    addr = s
    if "[" in addr:
        addr = addr[:addr.index("[")]
    src_is_var = addr.isidentifier() or addr == "$"
    if src_is_var:
        addr, n = addr_from_var(s, scopes)
    else:
        n = -1
    return (src_is_var, addr, n)

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
                "vars": scope.vars
            }
            scopes.append(scope)
            print_indented(blks, f"{codegen.cell_type} *{scope['name']} = {codegen.buf_name} + {base + offset};")
        elif op == "at":
            addrs = cast(AddrSelectorArgs, args)
            sel = cast(Expr, addrs.addrs[0])
            if sel.op == "signed":
                print_indented(blks, f"p {sel.args[0]}= {sel.args[1].to_bfhla()};")
            else:
                src_is_var, src_addr, offset = sanitize(sel.to_bfhla(), scopes)
                print_indented(blks, f"p = {codegen.buf_name} + {offset};")

        elif op == "config":
            pass
        elif op in ["move", "copy"]:
            assign_pair = cast(AssignArgs, args)
            src_is_var, src_addr, offset = sanitize(assign_pair.src.to_bfhla(), scopes)

            for dst in assign_pair.dsts:
                addr, offset = addr_from_var(dst.addr(), scopes)

                s = str(addr)
                s += (" = " if dst.clear
                      else " += " if dst.multiplier >= 0
                      else " -= ")
                if abs(dst.multiplier) > 1:
                    s += f"{src_addr} * {abs(dst.multiplier)};"
                else:
                    s += f"{src_addr};"

                print_indented(blks, s)
            if op != "copy" and src_is_var:
                print_indented(blks, f"{src_addr} = 0;")
        elif op == "clear":
            addrs = cast(AddrSelectorArgs, args)
            for addr in addrs.addrs:
                addr, _ = addr_from_var(addr.to_bfhla(), scopes)
                print_indented(blks, f"{addr} = 0;")
        elif op == "input":
            addrs = cast(AddrSelectorArgs, args)
            addr, _ = addr_from_var(addrs.to_bfhla(), scopes)
            print_indented(blks, f"{addr} = getchar();")
        elif op == "print":
            addrs = cast(AddrSelectorArgs, args)
            addr, _ = addr_from_var(addrs.to_bfhla(), scopes)
            print_indented(blks, f"putchar({addr});")
        elif op == "skipr":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"while (*p) p += {addrs.to_bfhla()};")
        elif op == "skipl":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"while (*p) p -= {addrs.to_bfhla()};")
        elif op == "bf":
            inline_bf = cast(BfArgs, args)
            src = inline_bf.text
            while len(src):
                m = re_bfrle_step.match(src)
                if not m:
                    break
                c, n, src = m.groups()
                if n == "":
                    n = 1
                if c == "+":
                    print_indented(blks, f"*p += {n};")
                elif c == "-":
                    print_indented(blks, f"*p -= {n};")
                elif c == ">":
                    print_indented(blks, f"p += {n};")
                elif c == "<":
                    print_indented(blks, f"p -= {n};")
                elif c == ",":
                    print_indented(blks, f"*p = getchar();")
                elif c == ",":
                    print_indented(blks, f"putchar(*p);")
                elif c == "[":
                    print_indented(blks, "while (*p) {")
                    blks += 1
                    blk_defers.append("")
                elif c == "]":
                    blks -= 1
                    blk_defers.pop()
                    print_indented(blks, "}")
        elif op == "balanced_loop_at":
            addrs = cast(AddrSelectorArgs, args)
            addr = addrs.to_bfhla()
            _, addr, offset = sanitize(addr, scopes)
            print_indented(blks, f"while ({addr}) {{")
            blks += 1
            blk_defers.append("")
        elif op == "ifnz":
            addrs = cast(AddrSelectorArgs, args)
            addr = addrs.to_bfhla()
            _, addr, offset = sanitize(addr, scopes)
            print_indented(blks, f"if ({addr}) {{")
            blks += 1
            blk_defers.append(f"{addr} = 0;")
        elif op == "predec_for":
            addrs = cast(AddrSelectorArgs, args)
            addr = addrs.to_bfhla()
            _, addr, offset = sanitize(addr, scopes)
            print_indented(blks, f"for (; {addr}; --{addr}) {{")
            blks += 1
            blk_defers.append("")
        elif op == "postdec_for":
            addrs = cast(AddrSelectorArgs, args)
            addr = addrs.to_bfhla()
            _, addr, offset = sanitize(addr, scopes)
            print_indented(blks, f"while ({addr}) {{")
            blks += 1
            print_indented(blks, f"--{addr};")
            blk_defers.append("")
        elif op == "balanced_loop":
            print_indented(blks, "while (p[0]) {")
            blks += 1
            blk_defers.append("")
        elif op == "loop":
            print_indented(blks, "while (*p) {")
            blks += 1
            blk_defers.append("")
        elif op == "end":
            s = blk_defers.pop()
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
