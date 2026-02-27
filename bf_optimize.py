from typing import cast, Union
import re
import bf_config
from bfhla_struct import *
import bf_config
import bf_parser
import bf_analyser


if __name__ == "__main__":
    import sys

    src = [*bf_parser.load_bf(input)]
    bf_analyser.optimize_bf(src)
    s = bf_analyser.bfrle_to_bf(src)

    for i in range(0, len(s), bf_config.codegen.max_line_col):
        print(s[i:i + bf_config.codegen.max_line_col])
