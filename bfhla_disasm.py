
from typing import Generator, Tuple

# least version without any scope-inference

INDENT_UNIT = "    "
BUF_SIZE = 32767
NAMED_VARS = ["x", "y", "z"]


def var_name(addr: int) -> str:
    if addr < len(NAMED_VARS):
        return NAMED_VARS[addr]

    return f"global[{addr}]"

def selector(addr0: int, addr1: int):
    if addr0 < 0 or addr1 < 0:
        return ""
    elif addr0 < addr1:
        return f" >{addr1 - addr0}"
    elif addr0 > addr1:
        return f" <{addr0 - addr1}"
    else:
        return ""

def check_balanced_span(src: list, start: int) -> Tuple[bool, int]:
    addr = 0
    i = start

    while i < len(src):
        op, arg = src[i]
        if op == ">":
            addr += arg
        elif op == "<":
            addr -= arg
        elif op == "[":
            is_balanced, j = check_balanced_span(src, i + 1)
            if not is_balanced:
                return False, 0
            i = j
            continue
        elif op == "]":
            i += 1
            break

        i += 1

    return (addr == 0), i

def print_indented(blks: list[int], s: str) -> str:
    print(INDENT_UNIT * (len(blks) - 1) + s)

def disasm(src):
    addr = 0
    blks = [0]

    print(f"scope global[{BUF_SIZE}] = x, y, z")

    i = 0
    while i < len(src):
        op, arg = src[i]

        if op in ["+", "-"]:
            if addr == -1:
                print_indented(blks, f"bf {op}{arg}")
            else:
                print_indented(blks, f"move {var_name(addr)}{op} = {arg}")
        elif op == "0":
            if addr == -1:
                print_indented(blks, f"bf [-]")
            elif len(src) > i + 1 and src[i + 1][0] == "+":
                print_indented(blks, f"move {var_name(addr)} = {src[i + 1][1]}")
                i += 1
            else:
                print_indented(blks, f"move {var_name(addr)} = 0")
        elif op == ">":
            if addr == -1:
                print_indented(blks, f"bf >{arg}")
            else:
                addr += 1
        elif op == "<":
            if addr == -1:
                print_indented(blks, f"bf <{arg}")
            else:
                addr -= 1
        elif op == ",":
            if addr == -1:
                print_indented(blks, f"bf ,")
            else:
                print_indented(blks, f"input {var_name(addr)}")
        elif op == ".":
            if addr == -1:
                print_indented(blks, f"bf .")
            else:
                print_indented(blks, f"print {var_name(addr)}")
        elif op == "[":
            is_balanced, _ = check_balanced_span(src, i + 1)
            if is_balanced and addr != -1:
                print_indented(blks, f"balanced_loop_at {var_name(addr)}")
                blks.append(addr)
            else:
                print_indented(blks, f"bf {selector(blks[-1], addr)} [")
                addr = -1
        elif op == "]":

            if addr == -1:
                print_indented(blks, f"bf ]")
            elif len(blks) <= 1:
                print_indented(blks, f"# error at {i}: unmatched ']'")
                return
            else:
                addr2 = blks.pop()
                if addr != addr2:
                    print_indented(blks, f"error at {i}: unbalanced '[]', any internal error")
                    addr = -1
                else:
                    print_indented(blks, f"end")

        i += 1

def load():
    try:
        while True:
            line = input().strip()
            print(f"# {line}")

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
    disasm([*load()])
