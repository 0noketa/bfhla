from typing import cast
import re
import bf_config
from bfhla_struct import *
import bf_config
import bf_parser
import bf_analyser


if __name__ == "__main__":
    import sys

    target = "bf"
    w = bf_config.codegen.max_line_col

    src = [*bf_parser.load_bf(input)]
    bf_analyser.optimize_bf(src)

    for arg in sys.argv[1:]:
        if arg in ("-h", "-?", "/?", "/h", "-help", "--help"):
            print(f"python {sys.argv[0]} [-tTARGET] [-wWIDTH] < *.bf > (*.bf|*.bfrle)")
            print(f"  targets: bf, bfrle: suffix, bfrlep: prefix")
        elif arg.startswith("-t"):
            target = arg[2:]
        elif arg.startswith("-w"):
            w = min(int(arg[2:]), 1)

    if target == "bf":
        s = bf_analyser.bfir_to_bf(src)
    elif target == "bfrlep":
        s = bf_analyser.bfir_to_bfrle(src, suffix=False)
    elif target == "bfrle":
        s = bf_analyser.bfir_to_bfrle(src, suffix=True)

    for i in range(0, len(s), w):
        print(s[i:i + w])
