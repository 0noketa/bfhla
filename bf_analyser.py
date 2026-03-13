
from typing import Tuple, Callable, Optional

# every list[tuple[str, int]] means BF-RLE in list of tuple form
# includes command "0" that means "[-]" and will be replaced with "-" when it was printed.

# macro instructions:
#   0: "[-]"
#   ptrmul: on clean mem, "[[" + ">"*n + "+" "<"*n "-]" + ">"*n "-]"
#   skipr: "[" + ">"*n + "]"
#   skipl: "[" + "<"*n + "]"
#   putsr: "[." + ">"*n + "]"
#   putsl: "[." + "<"*n + "]"

def check_skip(src: list[tuple[str, int]], start: int) -> Tuple[bool, int, int]:
    addr = 0
    start += 1

    for i, (op, arg) in enumerate(src[start:], start):
        if op == ">":
            addr += arg
        elif op == "<":
            addr -= arg
        elif op == "]":
            return True, addr, i + 1
        else:
            break

    return False, 0, start

def is_skip(src: list[Tuple[str, int]], start: int) -> bool:
    if len(src) <= start + 2 or src[start][0] != "[":
        return False

    cond, n, i = check_skip(src, start)
    return cond


def check_balanced_span(src: list[tuple[str, int]], start: int) -> Tuple[bool, int]:
    """result: (is_balanced, next to last step of span)"""
    addr = 0
    i = start

    while i < len(src):
        op, arg = src[i]
        if op == ">":
            addr += arg
        elif op == "<":
            addr -= arg
        elif op == "[":
            balanced, j = check_balanced_loop(src, i)
            if not balanced:
                break

            i = j
            continue
        elif op == "]":
            break

        i += 1

    return (addr == 0), i

def check_balanced_loop(src: list[tuple[str, int]], start: int) -> Tuple[bool, int]:
    """result: (is_balanced, next to ']')"""
    if len(src) <= start + 1 or src[start][0] != "[":
        return False, start

    cond, i = check_balanced_span(src, start + 1)
    return cond and i < len(src) and src[i][0] == "]", i + 1

def is_balanced_loop(src: list[Tuple[str, int]], start: int) -> bool:
    if len(src) <= start + 1 or src[start][0] != "[":
        return False

    cond, i = check_balanced_loop(src, start)
    return cond


def calc_move(src: list[Tuple[str, int]], start: int, base_addr: int = 0, memory: Optional[list[int]] = None) -> Tuple[bool, int, list[int], int]:
    """result: (is_move, base_addr in memory_map, mempry_map, next)"""
    if not is_balanced_loop(src, start):
        return False, 0, [], 0

    _, end = check_balanced_loop(src, start)

    if memory is None:
        memory = [0]

    addr = base_addr
    for i in range(start + 1, end):
        op, arg = src[i]
        if op == ">":
            addr += arg
            if addr >= len(memory):
                memory.extend([0] * (addr - len(memory) + 1))
        elif op == "<":
            addr -= arg
            if addr < 0:
                base_addr -= addr
                memory = [0] * (-addr) + memory
                addr = 0
        elif op == "+":
            memory[addr] += arg
        elif op == "-":
            memory[addr] -= arg
        elif op in ["[", ",", ".", "0"]:
            return False, 0, [], 0
        elif op == "]":
            i += 1
            break

    return (memory[base_addr] == -1), addr, memory, i

def is_move(src: list[Tuple[str, int]], start: int) -> bool:
    comd, _, _, _ = calc_move(src, start)
    return comd


def optimize_bf(src: list[Tuple[str, int]]):
    i = 0
    while i + 1 < len(src):
        it = src[i]
        next = src[i + 1]

        if it[0] not in ("+", "-", ">", "<", ",", ".", "[", "]", "0"):
            src[i] = next
            src.pop(i + 1)
            continue
        elif it[0] == next[0] and it[0] in ("+", "-", ">", "<"):
            src[i] = (it[0], it[1] + next[1])
            src.pop(i + 1)
            continue
        elif it[0] in ("+", "-") and next[0] == "0":
            src[i] = next
            src.pop(i + 1)
            continue
        elif i + 2 < len(src) and it[0] == "[" and next[0] == "-" and src[i + 2][0] == "]":
            src[i] = ("0", 0)
            src.pop(i + 1)
            src.pop(i + 1)
            continue

        op_pair = set((it[0], next[0]))
        if op_pair in (set((">", "<")), set(("+", "-"))):
            if it[1] >= next[1]:
                src[i] = (it[0], it[1] - next[1])
                src.pop(i + 1)
                if src[i][1] == 0:
                    src.pop(i)
                    if i > 0:
                        i -= 1
                continue
            else:
                src[i] = (next[0], next[1] - it[1])
                src.pop(i + 1)

                if i > 0:
                    i -= 1
                continue
        i += 1

def bfir_to_bfrle(src: list[Tuple[str, int]], suffix=True) -> str:
    s = ""
    for op, n in src:
        if op == "0":
            s += "[-]"
        elif op in "+-><":
            s += f"{op}{n}" if suffix else f"{n}{op}"
        else:
            s += op
    return s

def bfir_to_bf(src: list[Tuple[str, int]]) -> str:
    s = ""
    for op, n in src:
        if op == "0":
            s += "[-]"
        elif op in "+-><":
            s += op * n
        else:
            s += op
    return s

def bfrle_highlight(src: list[Tuple[str, int]], pos: int, surrounding_steps=8, highlight: Optional[Callable[[str], str]]=None) -> str:
    n = surrounding_steps
    s = bfir_to_bfrle(src[:pos][-n:])
    if highlight is not None:
        s += highlight(bfir_to_bfrle(src[pos:pos + 1]))
    else:
        s += f" *{bfir_to_bfrle(src[pos:pos + 1])}* "
    s += bfir_to_bfrle(src[pos + 1:][:n])
    return s
