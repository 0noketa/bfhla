
from typing import Tuple
import bf_analyser
from bfhla_config import *
from bfhla_struct import *
import bfhla_analyser
import codegen_bfhla
import codegen_bf

# least version without any scope-inference
# current version disassembles only codes with balanced loops and static addressing



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





def disasm(src: list[tuple[str, int]]) -> list[IrStep]:
    addr = 0
    blks = [0]
    dst = []

    dst.append(IrStep("config", ConfigArgs("assign_method", "move")))
    dst.append(IrStep("scope", ScopeDeclArgs(
        GLOBAL_SCOPE_NAME,
        ConstExpr("num", value=BUF_SIZE),
        ConstExpr("num", value=0),
        ConstExpr("num", value=0),
        NAMED_VARS
    )))

    i = 0
    while i < len(src):
        op, arg = src[i]
        ins = IrStep("error", RawArgs({"src": f"{op}"}))

        if op in ["+", "-"]:
            if addr == -1:
                ins = IrStep("bf", RawArgs({"code": bfrle(op, arg)}))
            else:
                ins = IrStep("move", AssignArgs(
                    [LValue([var_name(addr)], multiplier=1 if op == "+" else -1)],
                    str(arg)
                ))
        elif op == "0":
            if addr == -1:
                ins = IrStep("bf", RawArgs({"code": "[-]"}))
            elif len(src) > i + 1 and src[i + 1][0] == "+":
                ins = IrStep("move", AssignArgs(
                    [LValue([var_name(addr)], clear=True)],
                    str(src[i + 1][1])
                ))
                i += 1
            else:
                ins = IrStep("clear", AddrSelectorArgs([var_name(addr)]))
        elif op == ">":
            if addr == -1:
                ins = IrStep("at", AddrSelectorArgs([f"+{arg}"]))
                # ins = IrStep("bf", {"code": bfrle(">", arg)})
            else:
                addr += arg
                i += 1
                continue
        elif op == "<":
            if addr == -1:
                ins = IrStep("at", AddrSelectorArgs([f"-{arg}"]))
                # ins = IrStep("bf", RawArgs({"code": bfrle("<", arg)}))
            else:
                addr -= arg
                i += 1
                continue
        elif op == ",":
            if addr == -1:
                ins = IrStep("bf", RawArgs({"code": ","}))
            else:
                ins = IrStep("input", AddrSelectorArgs([var_name(addr)]))
        elif op == ".":
            if addr == -1:
                ins = IrStep("bf", RawArgs({"code": "."}))
            else:
                ins = IrStep("print", AddrSelectorArgs([var_name(addr)]))
        elif op == "[":
            if bf_analyser.is_skip(src, i):
                _, n, i = bf_analyser.check_skip(src, i)
                ins = IrStep(("skipr" if n > 0 else "skipl"), RawArgs({"count": abs(n)}))
                dst.append(ins)
                addr = -1
                continue
            elif bf_analyser.is_move(src, i):
                _, base_addr, memory, i = bf_analyser.calc_move(src, i)
                ins = bfhla_analyser.decode_move(addr, base_addr, memory)
                dst.append(ins)
                continue
            elif bf_analyser.is_balanced_loop(src, i):
                if addr != -1:
                    ins = IrStep("balanced_loop_at", AddrSelectorArgs([var_name(addr)]))
                else:
                    ins = IrStep("balanced_loop", RawArgs({}))
                blks.append(addr)
            else:
                if addr != -1:
                    ins = IrStep("at", AddrSelectorArgs([var_name(addr)]))
                    dst.append(ins)
                ins = IrStep("loop", RawArgs({}))
                addr = -1
        elif op == "]":
            if addr == -1:
                ins = IrStep("end", RawArgs({}))
            elif len(blks) <= 1:
                ins = IrStep("comment", RawArgs({"text": f" error at {i}: unmatched ']'"}))
                dst.append(ins)
                return
            else:
                addr2 = blks.pop()
                if addr != addr2:
                    ins = IrStep("comment", RawArgs({"text": f" error at {i}: unbalanced '[]', any internal error"}))
                    addr = -1
                else:
                    ins = IrStep("end", RawArgs({}))
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
    codegen_bfhla.print_bfhla(ir)
