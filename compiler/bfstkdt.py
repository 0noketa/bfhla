
# DSL(simple decision tree with messages) to BFStack
#   the language can not handle any loop. can not memory any data. use code as data.
#   strings can contain escape-sequence (only for double-quatation, linefeed and tab).
# language:
#   print text
#     print text. text can be any of symbol, charcode, string.
#   println text
#     print text and newline.
#   readln
#     ignore until next EOL.
#   ( c ?
#     "if-then". if input does not equal to c, skip until ":" or ")".
#     c can be any of charcode or striing (uses first char).
#   :
#     "else". skip until ")".
#   )
#     end of if-block.
from typing import cast
import re
import bfstack

re_tkn = re.compile(r"""\s*(\[|!|\]|\(|\?|:|\)|[0-9]+|[a-zA-Z_][a-zA-Z_0-9]*|"(?:\\"|[^"])+")(.*)""")


def tokenize(src: str) -> list[str]:
    dst = []
    while len(src):
        m = re_tkn.match(src)
        if not m:
            break

        tkn, rest = m.groups()
        src = rest
        dst.append(tkn)

    return dst

def load() -> list[str]:
    dst = []
    while True:
        src = sys.stdin.readline()
        if src == "":
            break

        src = src.strip()
        if src == "":
            continue
        if src.startswith("#"):
            continue

        dst.extend(tokenize(src))

    return dst

def decode_str(src: str) -> str:
    if not src.startswith('"'):
        return src

    src = src.replace('\\"', '"')
    src = src.replace('\\n', '\n')
    src = src.replace('\\t', '\t')

    return src[1:-1]

def parse(src: list[str]) -> list[tuple[str, str | int]]:
    dst = []
    i = 0
    while i < len(src):
        if i + 1 < len(src) and src[i] in ["print", "println"]:
            arg = src[i + 1]
            if arg.isdigit():
                txt = chr(int(arg))
            elif arg.startswith('"'):
                txt = decode_str(arg)
            else:
                txt = arg

            if src[i] == "println":
                txt += "\n"

            dst.append(("print", txt))

            i += 2
            continue

        if i + 2 < len(src) and src[i] == "(" and src[i + 2] == "?":
            arg = src[i + 1]

            if arg.isdigit():
                n = int(arg)
            elif arg.startswith('"'):
                n = ord(decode_str(arg)[0])
            else:
                n = 0
            
            dst.append(("if", n))
            i += 3
            continue

        if src[i] == "readln":
            dst.append(("readln", 0))
        elif src[i] == ":":
            dst.append(("else", 0))
        elif src[i] == ")":
            dst.append(("end", 0))
        elif src[i] == "[":
            dst.append(("do", 0))
        elif src[i] == "]":
            dst.append(("end", 0))

        i += 1

    return dst

def find_step(code: list[tuple[str, str | int]], name: str, start: int = 0) -> int:
    dpt = 0
    for i, (op, arg) in enumerate(code[start:], start=start):
        if op == name and dpt == 0:
            return i

        if op in ["if", "do"]:
            dpt += 1
        if op == "end":
            dpt -= 1

    return -1

def compile_parsed(code: list[tuple[str, str|int]], indent=0) -> list[str]:
    dst = []

    idt = "    " * indent

    i = 0
    while i < len(code):
        op, arg = code[i]

        if op == "print":
            s = bfstack.txt2bfstack(cast(str, arg))
            dst.append(idt + "print")
            dst.append(".\n".join(s.split(".")))
            dst.append(idt + "end print")
            i += 1
            continue

        if op == "if":
            n = cast(int, arg)

            j = find_step(code, "else", i + 1)
            if j != -1:
                k = find_step(code, "end", j + 1)
                if k == -1:
                    raise Exception("no end for if-else-block")

                dst.append(idt + f"ifneq {n} >+," + ("-" * n) + "[<->")
                dst.extend(compile_parsed(code[j + 1:k], indent + 1))
                dst.append(idt + "else ] <[")
                dst.extend(compile_parsed(code[i + 1:j], indent + 1))
                dst.append(idt + "fi -]<")

                i = k + 1
                continue

            k = find_step(code, "end", i + 1)
            if k == -1:
                raise Exception("no end for if-block")

            dst.append(idt + f"ifneq {n} >+," + ("-" * n) + "[<->] <[")
            dst.extend(compile_parsed(code[i + 1:k], indent + 1))
            dst.append(idt + "fi -]<")

            i = k + 1
            continue

        if op == "readln":
            dst.append(",----- -----[<,----- -----]<")

        i += 1

    return dst

def compile(src: list[str]) -> list[str]:
    code = parse(src)
    return compile_parsed(code)


if __name__ == "__main__":
    import sys

    src = load()
    code = compile(src)
    for s in code:
        print(s)


# how to implement switch
#
# stack: other, eq0, eq1, eq2, input
# >+>+>+>+>,
# [ neq0
#     -[ neq1
#        -[ neq2
#             <<<<<>>>>> clear
#         ]
#         <[ eq2
#             user_code_ifeq2
#             <<<<>>>> clear
#         ]>
#     ]
#     <<[ eq1
#         user_code_ifeq1
#         <<<>>> clear
#     ]>>
# ]
# <<<[ eq0
#     user_code_ifeq1
#     <<>> clear
# ]>>>
# <<<<[ otherwise
#     user_code_ifotherwise
#     <> clear
# ]>>>>
# <<<<
