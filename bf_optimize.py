from typing import cast
import re
import config.bf as bf_config
from bfhla.struct import *
import bf.parser as bf_parser
import bf.analyser as bf_analyser


if __name__ == "__main__":
    import sys

    target = "bf"
    w = bf_config.codegen.max_line_col

    for arg in sys.argv[1:]:
        if arg in ("-h", "-?", "/?", "/h", "-help", "--help"):
            print(f"python {sys.argv[0]} [-tTARGET] [-wWIDTH] < *.bf > (*.bf|*.bfrle)")
            print(f"  targets: bf, bfrle: suffix, bfrlep: prefix")
            sys.exit(0)
        elif arg.startswith("-t"):
            target = arg[2:]
        elif arg.startswith("-w"):
            w = min(int(arg[2:]), 1)

    src = [*bf_parser.load_bf(sys.stdin)]
    bf_analyser.optimize_bf(src)

    if target == "bf":
        s = bf_analyser.bfir_to_bf(src)
    elif target == "bfrlep":
        s = bf_analyser.bfir_to_bfrle(src, suffix=False)
    elif target == "bfrle":
        s = bf_analyser.bfir_to_bfrle(src, suffix=True)

    for i in range(0, len(s), w):
        print(s[i:i + w])
