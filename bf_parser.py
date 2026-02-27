
from typing import Tuple, Generator


def load_bf(input) -> Generator[Tuple[str, int]]:
    try:
        while True:
            line = input().strip()

            while line:
                c = line[0]
                if c in "+-><":
                    arg = 0
                    while line.startswith(c):
                        line = line[1:]
                        arg += 1
                    yield (c, arg)
                elif line.startswith("[-]"):
                    line = line[3:]
                    yield ("0", 0)
                elif c in ",.[]":
                    line = line[1:]
                    yield (c, 0)
                else:
                    line = line[1:]
    except EOFError:
        pass

