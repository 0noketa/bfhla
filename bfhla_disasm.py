
from typing import Tuple
import bf_analyser
from bfhla_config import *
from bfhla_struct import *
import bfhla_analyser

# least version without any scope-inference
# current version disassembles only codes with balanced loops and static addressing


# currently, semantic analyser can detect blocks in the form of:
# balanced_loop_at: every "[]" that keeps current address.
# for_range0: inside block, last 0 is visible. balanced loop in the form of "[- code]".
# for_range1: inside block, first value is visible. balanced loop in the form of "[code -]".
# ifnz: balanced loop in the form of "[code [-]]".
# # ifnz0: balanced loop in the form of "[[-] code]".
# # ifneq: balanced loop in the form of "-n [code [-]]".


def bfrle(cmd, n) -> str:
    if n == 0:
        return ""

    if NO_BFRLE:
        return cmd * n

    return cmd + (f"{n}" if n > 1 else "")

def selector(from_: int, to_: int):
    n = abs(to_ - from_)
    if from_ < 0 or to_ < 0:
        return ""
    elif from_ < to_:
        return bfrle(">", n)
    elif from_ > to_:
        return bfrle("<", n)
    else:
        return ""


def print_indented(i: int, s: str) -> str:
    print(INDENT_UNIT * i + s)


def print_ir(code: list[IrStep]):
    blks = 0

    for step in code:
        op, args = step.get_pair()
        if op == "scope":
            print_indented(blks, f"scope {args['name']}[{args['size']}] = {', '.join(args['vars'])}")
        elif op == "config":
            print_indented(blks, f"config {args['name']} = {args['value']}")
        elif op == "move":
            dst = ", ".join(args["dst"])
            prefix = "move " if EXPLICIT_MOVE else ""
            print_indented(blks, f"{prefix}{dst} = {args['src']}")
        elif op == "copy":
            dst = ", ".join(args["dst"])
            print_indented(blks, f"copy {dst} = {args['src']}")
        elif op == "clear":
            dst = ", ".join(args["dst"])
            print_indented(blks, f"clear {dst}")
        elif op == "input":
            dst = ", ".join(args["dst"])
            print_indented(blks, f"input {dst}")
        elif op == "print":
            src = ", ".join(args["src"])
            print_indented(blks, f"print {src}")
        elif op == "bf":
            print_indented(blks, f"bf {args['code']}")
        elif op == "balanced_loop_at":
            print_indented(blks, f"balanced_loop_at {args['addr']}")
            blks += 1
        elif op == "ifnz":
            print_indented(blks, f"ifnz {args['addr']}")
            blks += 1
        elif op == "for_range0":
            print_indented(blks, f"for_range0 {args['addr']}")
            blks += 1
        elif op == "for_range1":
            print_indented(blks, f"for_range1 {args['addr']}")
            blks += 1
        elif op == "end":
            blks -= 1
            print_indented(blks, "end")
        elif op == "comment":
            print_indented(blks, args["text"])
        elif op == "error":
            print_indented(blks, f"error {args['src']}")
        else:
            print_indented(blks, f"# unknown instruction: {op}")



def disasm(src: list[tuple[str, int]]) -> list[IrStep]:
    addr = 0
    blks = [0]
    dst = []

    dst.append(IrStep("config", {"name": "assign_method", "value": "move"}))
    dst.append(IrStep("scope", {"name": GLOBAL_SCOPE_NAME, "size": BUF_SIZE, "vars": NAMED_VARS}))

    i = 0
    while i < len(src):
        op, arg = src[i]
        ins = IrStep("error", {"src": f"{op}"})

        if op in ["+", "-"]:
            if addr == -1:
                ins = IrStep("bf", {"code": bfrle(op, arg)})
            else:
                ins = IrStep("move", {"dst": [var_name(addr) + op], "src": str(arg)})
        elif op == "0":
            if addr == -1:
                ins = IrStep("bf", {"code": "[-]"})
            elif len(src) > i + 1 and src[i + 1][0] == "+":
                ins = IrStep("move", {"dst": [var_name(addr)], "src": f"{src[i + 1][1]}"})
                i += 1
            else:
                ins = IrStep("clear", {"dst": [var_name(addr)]})
        elif op == ">":
            if addr == -1:
                ins = IrStep("bf", {"code": bfrle(">", arg)})
            else:
                addr += arg
                i += 1
                continue
        elif op == "<":
            if addr == -1:
                ins = IrStep("bf", {"code": bfrle("<", arg)})
            else:
                addr -= arg
                i += 1
                continue
        elif op == ",":
            if addr == -1:
                ins = IrStep("bf", {"code": ","})
            else:
                ins = IrStep("input", {"dst": [f"{var_name(addr)}"]})
        elif op == ".":
            if addr == -1:
                ins = IrStep("bf", {"code": "."})
            else:
                ins = IrStep("print", {"src": [f"{var_name(addr)}"]})
        elif op == "[":
            if addr != -1 and bf_analyser.is_move(src, i):
                _, base_addr, memory, i = bf_analyser.calc_move(src, i)
                ins = bfhla_analyser.decode_move(addr, base_addr, memory)
                dst.append(ins)
                continue
            elif addr != -1 and bf_analyser.is_balanced_loop(src, i):
                ins = IrStep("balanced_loop_at", {"addr": var_name(addr)})
                blks.append(addr)
            else:
                ins = IrStep("bf", {"code": f"{selector(blks[-1], addr)}["})
                addr = -1
        elif op == "]":
            if addr == -1:
                ins = IrStep("bf", {"code": "]"})
            elif len(blks) <= 1:
                ins = IrStep("comment", {"text": f" error at {i}: unmatched ']'"})
                dst.append(ins)
                return
            else:
                addr2 = blks.pop()
                if addr != addr2:
                    ins = IrStep("comment", {"text": f" error at {i}: unbalanced '[]', any internal error"})
                    addr = -1
                else:
                    ins = IrStep("end", {})
        else:
            i += 1
            continue

        dst.append(ins)
        i += 1

    return dst

def load():
    try:
        while True:
            line = input().strip()
            # print(f"# {line}")

            while line:
                c = line[0]
                if c in "+-><":
                    arg = 0
                    while line.startswith(c):
                        line = line[1:]
                        arg += 1
                    yield (c, arg)
                elif line.startswith("[-]"):
                    line = line[3:]
                    yield ("0", 0)
                else:
                    line = line[1:]
                    yield (c, 0)
    except EOFError:
        pass


if __name__ == "__main__":
    ir = disasm([*load()])
    ir = bfhla_analyser.merge_inline_bf(ir)
    if not NO_SEMANTIC_ANALYSER:
        ir = bfhla_analyser.rewrite_ir(ir)
    print_ir(ir)
