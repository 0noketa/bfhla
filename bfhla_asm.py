from typing import cast
import re
import config.bfhla as bfhla_config
from bfhla.struct import *
import bf.parser as bf_parser
import bfhla.parser as bfhla_parser


if __name__ == "__main__":
    import sys

    target = "bfhla"

    for arg in sys.argv:
        if arg.startswith("-t"):
            target = arg[2:]
        elif arg.startswith("--no_semantic_analyser"):
            bfhla_config.disasm.replace("no_semantic_analyser", True)
        elif arg.startswith("--indent_unit="):
            bfhla_config.codegen.replace("indent_unit", arg[len("--indent_unit="):])
        elif arg.startswith("--max_inline_bf_length="):
            bfhla_config.codegen.replace("max_inline_bf_length", int(arg[len("--max_inline_bf_length="):]))
        elif arg.startswith("--no_bfrle"):
            bfhla_config.codegen.replace("no_bfrle", True)
        elif arg.startswith("--buf_size="):
            bfhla_config.disasm.replace("buf_size", int(arg[len("--buf_size="):]))
        elif arg.startswith("--global_scope_name="):
            bfhla_config.disasm.replace("global_scope_name", arg[len("--global_scope_name="):])
        elif arg in ["-h", "--help"]:
            print("usage: bfhla_asm.py [options] < input.bfhla > output")
            print("options:")
            print("  -tTARGET, --target=TARGET    set target (default: bfhla)")
            print("  --no_semantic_analyser       outputs only raw loops")
            print("  --indent_unit=UNIT           set indent unit (default: 4 spaces)")
            print("  --max_inline_bf_length=N     merges inline BF until this length (default: 64)")
            print("  --no_bfrle                   disables BF-RLE(suffix) as inline BF")
            print("  --buf_size=N                 set buffer size for disasm (default: 32767)")
            print("  --global_scope_name=NAME     set global scope name for disasm (default: mem)")
            print("  -h, --help                   show this help message and exit")
            print("targets: assemblerfuck, bfhla, bf, c")
            sys.exit(0)

    src = sys.stdin.readlines()
    prog = bfhla_parser.parse_into_flat(src)

    if target == "assemblerfuck":
        import codegen.assemblerfuck
        codegen.assemblerfuck.print_assemblerfuck(prog)
    elif target == "bfhla":
        import codegen.bfhla
        codegen.bfhla.print_bfhla(prog)
    elif target == "bf":
        import codegen.bf
        codegen.bf.print_bf(prog)
    elif target == "c":
        import codegen.c
        codegen.c.print_c(prog)
    else:
        print(f"unknown target: {target}")
