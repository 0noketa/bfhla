
from typing import cast, Tuple
import config.bfhla as bfhla_config
from bfhla.struct import *


def print_indented(i: int, s: str):
    print(bfhla_config.codegen.indent_unit * i + s)


def print_bfhla(code: list[IrStep]):
    blks = 0

    for step in code:
        op, args = step.get_pair()
        if op == "scope":
            scope = cast(ScopeDeclArgs, args)
            size = scope.size.to_bfhla()
            base = scope.base.to_bfhla()
            offset = scope.offset.to_bfhla()

            loc = f" @ {base}+{offset}" if base != "0" and offset != "0" else ""
            print_indented(blks, f"scope {scope.name}[{size}]{loc} = {', '.join(scope.var_names())}")
        elif op == "at":
            addrs = cast(AddrSelectorArgs, args)
            sel = cast(Expr, addrs.addrs[0])
            if sel.op == "signed":
                print_indented(blks, f"at {sel.args[0]}{sel.args[1].to_bfhla()}")
            else:
                print_indented(blks, f"at {sel.to_bfhla()}")
        elif op == "config":
            conf = cast(ConfigArgs, args)
            print_indented(blks, f"config {conf.name} = {conf.value}")
        elif op == "move":
            assign_pair = cast(AssignArgs, args)
            prefix = "move " if bfhla_config.codegen.explicit_move else ""
            print_indented(blks, f"{prefix}{assign_pair.to_bfhla()}")
        elif op == "copy":
            assign_pair = cast(AssignArgs, args)
            print_indented(blks, f"copy {assign_pair.to_bfhla()}")
        elif op == "clear":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"clear {addrs.to_bfhla()}")
        elif op == "input":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"input {addrs.to_bfhla()}")
        elif op == "print":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"print {addrs.to_bfhla()}")
        elif op == "skipr":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"skipr {addrs.to_bfhla()}")
        elif op == "skipl":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"skipl {addrs.to_bfhla()}")
        elif op == "bf":
            inline_bf = cast(BfArgs, args)
            print_indented(blks, f"bf \"{inline_bf.to_bfhla()}\"")
        elif op == "balanced_loop_at":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"balanced_loop_at {addrs.to_bfhla()}")
            blks += 1
        elif op == "balanced_loop":
            print_indented(blks, f"balanced_loop")
            blks += 1
        elif op == "ifnz":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"ifnz {addrs.to_bfhla()}")
            blks += 1
        elif op == "predec_for":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"predec_for {addrs.to_bfhla()}")
            blks += 1
        elif op == "postdec_for":
            addrs = cast(AddrSelectorArgs, args)
            print_indented(blks, f"postdec_for {addrs.to_bfhla()}")
            blks += 1
        elif op == "loop":
            print_indented(blks, "loop")
            blks += 1
        elif op == "end":
            blks -= 1
            print_indented(blks, "end")
        elif op == "comment":
            cmt = cast(RawArgs, args)
            print_indented(blks, cmt.args["text"])
        elif op == "error":
            err = cast(RawArgs, args)
            print_indented(blks, f"error {err.args['src']}")
        else:
            print_indented(blks, f"# unknown instruction: {op}")
