
from typing import Tuple, Generator
import bf_analyser
import bf_parser
import bfhla_config
from bfhla_struct import *
import bfhla_analyser
import codegen_bfhla
import codegen_bf

# least version without any scope-inference
# current version disassembles only codes with balanced loops and static addressing

# bugs:
#   when program contains only balanced loops, last unused ">" and "<" will be ignored.
#   that canses error if output was linked.

def bfrle(cmd, n) -> str:
    if n == 0:
        return ""

    if bfhla_config.codegen.no_bfrle:
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
        bfhla_config.disasm.global_scope_name,
        Expr("num", value=bfhla_config.disasm.buf_size),
        Expr("num", value=0),
        Expr("num", value=0),
        list(map(VarDecl, bfhla_config.disasm.named_vars))
    )))

    i = 0
    while i < len(src):
        op, arg = src[i]
        ins = IrStep("error", RawArgs({"src": f"{op}"}))

        if op in ["+", "-"]:
            if addr == -1:
                ins = IrStep("bf", BfArgs([(op, arg)]))
            else:
                ins = IrStep("move", AssignArgs(
                    [LValue([var_name(addr)], multiplier=1 if op == "+" else -1)],
                    Expr.num_node(str(arg))
                ))
        elif op == "0":
            if addr == -1:
                ins = IrStep("clear", AddrSelectorArgs([
                    Expr.id_node("$[0]")
                ]))
            elif len(src) > i + 1 and src[i + 1][0] == "+":
                ins = IrStep("move", AssignArgs(
                    [LValue([var_name(addr)], clear=True)],
                    Expr.num_node(str(src[i + 1][1]))
                ))
                i += 1
            else:
                ins = IrStep("clear", AddrSelectorArgs([
                    Expr.id_node(var_name(addr))
                ]))
        elif op == ">":
            if addr == -1:
                sel = Expr("signed", ["+", Expr.num_node(str(arg))])
                ins = IrStep("at", AddrSelectorArgs([sel]))
            else:
                addr += arg
                i += 1
                continue
        elif op == "<":
            if addr != -1:
                if addr - arg < 0:
                    arg -= addr
                    addr = -1
                else:
                    addr -= arg

            if addr == -1:
                sel = Expr("signed", ["-", Expr.num_node(str(arg))])
                ins = IrStep("at", AddrSelectorArgs([sel]))
            else:
                i += 1
                continue
        elif op == ",":
            if addr == -1:
                ins = IrStep("bf", BfArgs([(",", 0)]))
            else:
                ins = IrStep("input", AddrSelectorArgs([
                    Expr.id_node(var_name(addr))
                ]))
        elif op == ".":
            if addr == -1:
                ins = IrStep("bf", BfArgs([(".", 0)]))
            else:
                ins = IrStep("print", AddrSelectorArgs([
                    Expr.id_node(var_name(addr))
                ]))
        elif op == "[":
            if bf_analyser.is_skip(src, i):
                _, n, i = bf_analyser.check_skip(src, i)
                sel = Expr.num_node(str(abs(n)))
                ins = IrStep(("skipr" if n > 0 else "skipl"), AddrSelectorArgs([sel]))
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
                    sel = Expr.id_node(var_name(addr))
                    ins = IrStep("balanced_loop_at", AddrSelectorArgs([sel]))
                else:
                    ins = IrStep("balanced_loop", RawArgs({}))
                blks.append(addr)
            else:
                if addr != -1:
                    sel = Expr.id_node(var_name(addr))
                    ins = IrStep("at", AddrSelectorArgs([sel]))
                    dst.append(ins)
                ins = IrStep("loop", RawArgs({}))
                addr = -1
        elif op == "]":
            if addr == -1:
                ins = IrStep("end", RawArgs({}))
            elif len(blks) <= 1:
                ins = IrStep("comment", RawArgs({"text": f" error at {i}: unmatched ']'"}))
                dst.append(ins)
                return dst
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


if __name__ == "__main__":
    import sys
    bf = [*bf_parser.load_bf(sys.stdin)]
    bf_analyser.optimize_bf(bf)
    ir = disasm(bf)
    ir = bfhla_analyser.merge_inline_bf(ir)
    if not bfhla_config.general.no_semantic_analyser:
        ir = bfhla_analyser.rewrite_ir(ir)
    codegen_bfhla.print_bfhla(ir)
