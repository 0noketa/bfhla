
from typing import Tuple
from bfhla_config import *
from bfhla_struct import *


BLOCK_HERDERS = ["balanced_loop_at", "ifnz", "for_range0", "for_range1"]


def find_block_end(src: list[IrStep], start: int) -> int:
    blks = 0
    for i in range(start, len(src)):
        op, _ = src[i].get_pair()
        if op in BLOCK_HERDERS:
            blks += 1
        elif op == "end":
            if blks == 0:
                return i
            blks -= 1

    return -1

def check_ifnz_block(code: list[IrStep], i: int) -> Tuple[bool, int]:
    if len(code) <= i + 1 or code[i].op != "balanced_loop_at":
        return False, 0

    j = find_block_end(code, i + 1)
    if (j != -1 and j - 1 >= i
            and code[j - 1].op == "clear"
            and len(code[j - 1].args["dst"]) == 1
            and code[j - 1].args["dst"][0] == code[i].args['addr']
            ):
        return True, j

    return False, 0
def is_ifnz_block(code: list[IrStep], i: int) -> bool:
    cond, _ = check_ifnz_block(code, i)
    return cond

def check_forrange0_block(code: list[IrStep], i: int) -> Tuple[bool, int]:
    if len(code) <= i + 1 or code[i].op != "balanced_loop_at":
        return False, 0

    if (i + 1 < len(code)  # ifnz0: balanced loop in the form of "[[-] code]".
            and code[i + 1].op == "move"
            and len(code[i + 1].args["dst"]) == 1
            and code[i + 1].args["src"] == "1"
            and code[i + 1].args["dst"][0] == f"{code[i].args['addr']}-"
            ):
        return True, i + 2

    j = find_block_end(code, i + 1)
    return False, j - 1 if j > i + 1 else j
def is_forrange0_block(code: list[IrStep], i: int) -> bool:
    cond, _ = check_forrange0_block(code, i)
    return cond

def check_forrange1_block(code: list[IrStep], i: int) -> Tuple[bool, int]:
    if len(code) <= i + 1 or code[i].op != "balanced_loop_at":
        return False, 0

    j = find_block_end(code, i + 1)
    if (j != -1 and j - 1 >= i
            and code[j - 1].op == "move"
            and len(code[j - 1].args["dst"]) == 1
            and code[j - 1].args["src"] == "1"
            and code[j - 1].args["dst"][0] == f"{code[i].args['addr']}-"
            ):
        return True, j

    return False, j
def is_forrange1_block(code: list[IrStep], i: int) -> bool:
    cond, _ = check_forrange1_block(code, i)
    return cond

def rewrite_ir(code: list[IrStep]) -> list[IrStep]:
    # import sys
    i = 0
    dst = []
    blacklist = []
    while i < len(code):
        op, args = code[i].get_pair()
        # sys.stderr.write(f"{i:03}: {op} {args}\n")

        if i in blacklist:
            blacklist.remove(i)
            i += 1
            continue

        if i + 1 < len(code):
            next = code[i + 1]
        else:
            next = None

        if op == "move" and len(args["dst"]) == 0:
            if not args["src"].isdigit():
                op = "clear"
                args = {"dst": args["src"]}

        # if op == "move" and i + 1 < len(code) and next.op == "move":
        #     pass
        if op == "clear":
            expected = [i + "+" for i in args["dst"]]
            if (next is not None and next.op == "move"
                    and len(next.args["dst"]) == len(expected)
                    and all(s in next.args["dst"] for s in expected)):

                op = "move"
                args = {"dst": args["dst"], "src": next.args["src"]}
                i += 1
        elif op == "balanced_loop_at" and is_ifnz_block(code, i):
            op = "ifnz"
            _, j = check_ifnz_block(code, i)
            blacklist.append(j - 1)
        elif op == "balanced_loop_at" and is_forrange0_block(code, i):
            op = "for_range0"
            _, j = check_forrange0_block(code, i)
            i += 1
        elif op == "balanced_loop_at" and is_forrange1_block(code, i):
            op = "for_range1"
            _, j = check_forrange1_block(code, i)
            blacklist.append(j - 1)

        dst.append(IrStep(op, args))
        i += 1

    return dst


def merge_inline_bf(code: list[IrStep]) -> list[IrStep]:
    i = 0
    dst = []
    while i < len(code):
        op, args = code[i].get_pair()

        if op == "bf":
            j = i + 1
            while j < len(code) and code[j].op == "bf":
                bf = args["code"] + code[j].args["code"]
                if len(bf) > MAX_INLINE_BF_LENGTH:
                    break

                args = {"code": bf}
                j += 1

            i = j - 1

        dst.append(IrStep(op, args))
        i += 1

    return dst


def decode_move(addr: int, base_addr: int, memory: list[int]) -> IrStep:
    dst = []
    for i in range(len(memory)):
        var_addr = addr + (i - base_addr)

        if i != base_addr:
            if memory[i] != 0 and KEEP_ALL_MOVE_DST:
                s = f"{var_name(var_addr)}" + ("+" if memory[i] >= 0 else "-")
                if abs(memory[i]) != 1:
                        s += f"{abs(memory[i])}"
                dst.append(s)

    return IrStep("move", {"dst": dst, "src": var_name(addr)})
