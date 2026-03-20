
# bfstack2bf: BFStack -> Brainfuck
# txt2bfstack: text -> BFStack
#
# Hurricane996 's BFStack
# https://esolangs.org/wiki/BFStack
#
# encodings:
#    None1 's <stack>+
#    https://esolangs.org/wiki/LstackG%2B
#    "[>,+.<]-" -> "<stack>+"


def run_with_list_io(src: str, input: list[int] = [], intput_start=0) -> tuple[int, list[int]]:
    """result: (next_index, output) if input is empty else (next_input_idx, output)"""
    input_idx = 0
    output = []
    stack = []
    i = 0
    while i < len(src):
        c = src[i]
        if c == ">":
            stack.append(0)
        elif c == "<":
            stack.pop()
        elif c == "+":
            stack[-1] = (stack[-1] + 1) & 0xFF
        elif c == "-":
            stack[-1] = (stack[-1] - 1) & 0xFF
        elif c == ",":
            stack.append(input[input_idx])
            input_idx += 1
        elif c == ".":
            output.append(stack[-1])
        elif c == "[":
            if stack[-1] == 0:
                dpt = 0
                while i < len(src):
                    c2 = src[i]
                    if c2 == "[":
                        dpt += 1
                    if c2 == "]":
                        if dpt == 0:
                            i += 1
                            break
                        dpt -= 1
                    i += 1
                continue
        elif c == "]":
            if stack[-1] != 0:
                dpt = 0
                while i >= 0:
                    c2 = src[i]
                    if c2 == "]":
                        dpt += 1
                    if c2 == "[":
                        if dpt == 0:
                            i += 2
                            break
                        dpt -= 1
                    i -= 1
                continue
        i += 1

    return input_idx, output

def bfstack2bf(src: str) -> str:
    dst = ""
    for c in src:
        if c == ">":
            dst += ">"
        elif c == "<":
            dst += "[-]<"
        elif c == "+":
            dst += "+"
        elif c == "-":
            dst += "-"
        elif c == ",":
            dst += ">,"
        elif c == ".":
            dst += "."
        elif c == "[":
            dst += "["
        elif c == "]":
            dst += "]"

    return dst

def txt2bfstack(src: str, it: int = -1) -> str:
    txt = list(map(ord, src))
    stk = [0 if it != -1 else it]
    dst = ">\n" if it == -1 else ""
    for c in txt:
        old = stk[0]

        if c < old:
            dst += "-" * (old - c)
        else:
            dst += "+" * (c - old)

        stk[0] = c

        dst += "."

    dst += "<" if it == -1 else ""
    return dst

if __name__ == "__main__":
    import sys
    cmd = "bfstack2bf"

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

    if cmd == "bfstack2bf":
        try:
            while True:
                src = input() + "\n"
                dst = bfstack2bf(src)
                print(dst)
        except:
            pass
    elif cmd == "txt2bfstack":
        it = 0
        try:
            while True:
                src = input() + "\n"
                dst = txt2bfstack(src, it)
                it = 10
                print(dst)
        except:
            pass
    else:
        print(f"python {sys.argv[0]} [cmd] [args]")
        print("cmd: txt2bfstack, bfstack2bf")
