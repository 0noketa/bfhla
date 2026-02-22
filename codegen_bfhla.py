
from typing import Tuple
from bfhla_config import *
from bfhla_struct import *


def print_indented(i: int, s: str) -> str:
    print(INDENT_UNIT * i + s)


def print_bfhla(code: list[IrStep]):
    blks = 0

    for step in code:
        op, args = step.get_pair()
        if op == "scope":
            loc = f" @ {args.base}+{args.offset}" if args.base != 0 and args.offset != 0 else ""
            print_indented(blks, f"scope {args.name}[{args.size}]{loc} = {', '.join(args.vars)}")
        elif op == "at":
            addrs: AddrSelectorArgs = args
            print_indented(blks, f"at {addrs.to_bfhla()}")
        elif op == "config":
            print_indented(blks, f"config {args.name} = {args.value}")
        elif op == "move":
            assign_pair: AssignArgs = args
            prefix = "move " if EXPLICIT_MOVE else ""
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
            print_indented(blks, f"skipr {args['count']}")
        elif op == "skipl":
            print_indented(blks, f"skipl {args['count']}")
        elif op == "bf":
            print_indented(blks, f"bf {args['code']}")
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
        elif op == "for_range0":
            addrs: AddrSelectorArgs = args
            print_indented(blks, f"for_range0 {addrs.to_bfhla()}")
            blks += 1
        elif op == "for_range1":
            addrs: AddrSelectorArgs = args
            print_indented(blks, f"for_range1 {addrs.to_bfhla()}")
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
