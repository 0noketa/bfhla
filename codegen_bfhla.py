
from typing import Tuple
from bfhla_config import *
from bfhla_struct import *


def print_indented(i: int, s: str) -> str:
    print(codegen.indent_unit * i + s)


def print_bfhla(code: list[IrStep]):
    blks = 0

    for step in code:
        op, args = step.get_pair()
        if op == "scope":
            scope: ScopeDeclArgs = args
            size = scope.size.to_bfhla()
            base = scope.base.to_bfhla()
            offset = scope.offset.to_bfhla()

            loc = f" @ {base}+{offset}" if base != "0" and offset != "0" else ""
            print_indented(blks, f"scope {scope.name}[{size}]{loc} = {', '.join(scope.vars)}")
        elif op == "at":
            addrs: AddrSelectorArgs = args
            sel: Expr = addrs.addrs[0]
            if sel.op == "signed":
                print_indented(blks, f"at {sel.args[0]}{sel.args[1].to_bfhla()}")
            else:
                print_indented(blks, f"at {sel.to_bfhla()}")
        elif op == "config":
            print_indented(blks, f"config {args.name} = {args.value}")
        elif op == "move":
            assign_pair: AssignArgs = args
            prefix = "move " if codegen.explicit_move else ""
            print_indented(blks, f"{prefix}{assign_pair.to_bfhla()}")
        elif op == "copy":
            assign_pair: AssignArgs = args
            print_indented(blks, f"copy {assign_pair.to_bfhla()}")
        elif op == "clear":
            addrs: AddrSelectorArgs = args
            print_indented(blks, f"clear {addrs.to_bfhla()}")
        elif op == "input":
            addrs: AddrSelectorArgs = args
            print_indented(blks, f"input {addrs.to_bfhla()}")
        elif op == "print":
            addrs: AddrSelectorArgs = args
            print_indented(blks, f"print {addrs.to_bfhla()}")
        elif op == "skipr":
            print_indented(blks, f"skipr {args.to_bfhla()}")
        elif op == "skipl":
            print_indented(blks, f"skipl {args.to_bfhla()}")
        elif op == "bf":
            inline_bf: BfArgs = args
            print_indented(blks, f"bf \"{inline_bf.to_bfhla()}\"")
        elif op == "balanced_loop_at":
            addrs: AddrSelectorArgs = args
            print_indented(blks, f"balanced_loop_at {addrs.to_bfhla()}")
            blks += 1
        elif op == "balanced_loop":
            print_indented(blks, f"balanced_loop")
            blks += 1
        elif op == "ifnz":
            addrs: AddrSelectorArgs = args
            print_indented(blks, f"ifnz {addrs.to_bfhla()}")
            blks += 1
        elif op == "predec_for":
            addrs: AddrSelectorArgs = args
            print_indented(blks, f"predec_for {addrs.to_bfhla()}")
            blks += 1
        elif op == "postdec_for":
            addrs: AddrSelectorArgs = args
            print_indented(blks, f"postdec_for {addrs.to_bfhla()}")
            blks += 1
        elif op == "loop":
            print_indented(blks, "loop")
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
