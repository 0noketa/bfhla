
from typing import cast, Tuple
import config.bfhla as bfhla_config
from bfhla.struct import *


# currently, semantic analyser can detect blocks in the form of:
#    balanced_loop: every "[]" that keeps current address.
#    balanced_loop_at: every "[]" that keeps current address. this version is only for visible scopes
#    for_range0: inside block, last 0 is visible. balanced loop in the form of "[- code]".
#    for_range1: inside block, first value is visible. balanced loop in the form of "[code -]".
#    ifnz: balanced loop in the form of "[code [-]]".
# #    ifnz0: balanced loop in the form of "[[-] code]".
# #    ifneq: balanced loop in the form of "-n [code [-]]".


BLOCK_HERDERS = ["balanced_loop", "balanced_loop_at", "ifnz", "for_range0", "for_range1"]


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
    if (j != -1 and j - 1 >= i):
            last_op = code[j - 1].op
            last_args = cast(AssignArgs, code[j - 1].args)
            if (last_op == "clear"
                    and len(last_args.addrs) == 1
                    and last_args.addrs[0] == code[i].args.addrs[0]
                    ):
                return True, j

    return False, 0
def is_ifnz_block(code: list[IrStep], i: int) -> bool:
    cond, _ = check_ifnz_block(code, i)
    return cond

def check_forrange0_block(code: list[IrStep], i: int) -> Tuple[bool, int]:
    if len(code) <= i + 1 or code[i].op != "balanced_loop_at":
        return False, 0

    if (i + 1 < len(code)):  # ifnz0: balanced loop in the form of "[[-] code]".
        first_op = code[i + 1].op
        first_args = cast(AssignArgs, code[i + 1].args)
        if(first_op == "move"
                and len(first_args.dsts) == 1
                and first_args.src == "1"
                and first_args.dsts[0].to_bfhla() == f"{code[i].args.addrs[0]}-"
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
    if (j != -1 and j - 1 >= i):
            last_op = code[j - 1].op
            last_args = cast(AssignArgs, code[j - 1].args)
            if(last_op == "move"
                    and len(last_args.dsts) == 1
                    and last_args.src == "1"
                    and last_args.dsts[0].to_bfhla() == f"{code[i].args.addrs[0]}-"
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

        if op == "move" and len(args.dsts) == 0 and type(args.src) is Expr:
            if not args.src.is_const():
                op = "clear"
                args = AddrSelectorArgs([args.src])

        if op == "move" and next is not None and next.op == "move":
            pass

        if op == "clear":
            expected = args.to_bfhla() + "+"

            if (next is not None and next.op == "move"
                    and type(next.args) == AssignArgs
                    and len(next.args.dsts) == 1
                    and next.args.dsts[0].to_bfhla() == expected):

                # this replacement corrupts code. check AssignArgs
                op = "move"
                args = AssignArgs([LValue([args.to_bfhla()], clear=True)], next.args.src)
                i += 1
        elif op == "balanced_loop_at" and is_ifnz_block(code, i):
            op = "ifnz"
            _, j = check_ifnz_block(code, i)
            blacklist.append(j - 1)
        elif op == "balanced_loop_at" and is_forrange0_block(code, i):
            op = "predec_for"
            _, j = check_forrange0_block(code, i)
            i += 1
        elif op == "balanced_loop_at" and is_forrange1_block(code, i):
            op = "postdec_for"
            _, j = check_forrange1_block(code, i)
            blacklist.append(j - 1)

        if op in ["copy", "move"] and type(args) is AssignArgs and len(args.dsts) == 0:
            op = "clear" 
            args = AddrSelectorArgs([args.src])

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
            bf = cast(BfArgs, args).bf
            while j < len(code) and code[j].op == "bf":
                bf += cast(BfArgs, code[j].args).bf
                if len(bf) > bfhla_config.MAX_INLINE_BF_LENGTH:
                    break

                j += 1

            i = j - 1

            dst.append(IrStep(op, BfArgs(bf)))
        else:
            dst.append(code[i])

        i += 1

    return dst


def decode_move(addr: int, base_addr: int, memory: list[int]) -> IrStep:
    """base_addr: pointer index on memory map"""
    dst = []
    if addr == -1:
        addr = 0
        fixed_addr = False
    else:
        fixed_addr = True

    for i in range(len(memory)):
        rel_addr = (i - base_addr)
        var_addr = addr + rel_addr

        if i != base_addr:
            if memory[i] != 0:
                dst_addr = var_name(var_addr) if fixed_addr else f"$[{var_addr}]"
                multiplier = memory[i]
                dst.append(LValue([dst_addr], multiplier=multiplier))

    if fixed_addr:
        src = var_name(addr)
    else:
        src = "$[0]"
    return IrStep("move", AssignArgs(dst, Expr.id_node(src)))
