
from typing import Tuple, Generator, TextIO
import re

re_bfrle_starts_with_unused_num = re.compile(r"^(\d+)([^+\-><].*)$")
re_bfrle_ends_with_unused_num = re.compile(r"^(.*[^+\-><])(\d+)$")
re_bfrle_starts_with_bf_without_num = re.compile(r"^([^+\-><]{1})([^0-9]+)(.*)$")
re_bfrle_ends_with_bf_without_num = re.compile(r"^(.*)([^0-9]+)([^+\-><]{1})$")
re_bfrle_suffix_step = re.compile(r"^(.{1}|\[\-\])(\d*)[^+\-><,\.\[\]]*(.*)$")
re_bfrle_prefix_step = re.compile(r"^(\d*)(.{1}|\[\-\])[^+\-><,\.\[\]]*(.*)$")
re_bfrle_step = re.compile(r"^(\d*)(.{1}|\[\-\])(\d*)[^+\-><,\.\[\]]*(.*)$")


def bf_to_bfir(s: str) -> list[Tuple[str, int]]:
    dst = []
    while s:
        c = s[0]
        if c in "+-><":
            arg = 0
            while s.startswith(c):
                s = s[1:]
                arg += 1
            dst.append((c, arg))
        elif s.startswith("[-]"):
            s = s[3:]
            dst.append(("0", 0))
        elif c in ",.[]":
            s = s[1:]
            dst.append((c, 0))
        else:
            s = s[1:]
    
    return dst

def load_bf(f: TextIO) -> list[Tuple[str, int]]:
    dst = []
    while not f.closed and f.readable():
        s = f.readline()
        if s == "":
            break

        dst.extend(bf_to_bfir(s.strip()))

    return dst


def load_bfrle(f: TextIO, mode="auto", ignore_eol=True, ignore_space=False) -> list[Tuple[str, int]]:
    """mode: any of\n
        - prefix: prefix-only\n
        - suffix: suffix-only\n
        - auto: basically suffix. but if unused number is followed by command, treats it as prefix notation. "3>+2-" is ["3>", "+2", "-"]\n
        ignore_eol: "+\\n2" becomes to "+2" if true\n
        ignore_space: "+ 2" becomes to "+2" if true
    """
    dst = []
    if not f.readable():
        return []

    src = [(s[:-1] if s.endswith("\n") else s) for s in f.readlines()]
    if ignore_space:
        src = [s.replace(" ", "") for s in src]

    if ignore_eol:
        if mode == "suffix":
            for i, line in enumerate(src[1:], start=1):
                m = re_bfrle_starts_with_unused_num.match(line)
                m2 = re_bfrle_ends_with_bf_without_num.match(src[i - 1])
                if m and m2:
                    num, rest = m.groups()
                    src[i - 1] += num
                    src[i] = rest
        elif mode == "prefix":
            for i, line in enumerate(src[:-1]):
                m = re_bfrle_ends_with_unused_num.match(line)
                m2 = re_bfrle_starts_with_bf_without_num.match(src[i + 1])
                if m and m2:
                    rest, num = m.groups()
                    src[i] = rest
                    src[i + 1] = num + src[i + 1]
        elif mode == "auto":
            for i, line in enumerate(src):
                if i > 0:
                    m = re_bfrle_starts_with_unused_num.match(line)
                    m2 = re_bfrle_ends_with_bf_without_num.match(src[i - 1])
                    if m and m2:
                        num, rest = m.groups()
                        src[i - 1] += num
                        src[i] = rest

                if i < len(src):
                    m = re_bfrle_ends_with_unused_num.match(line)
                    m2 = re_bfrle_starts_with_bf_without_num.match(src[i + 1])
                    if m and m2:
                        rest, num = m.groups()
                        src[i] = rest
                        src[i + 1] = num + src[i + 1]

    dst = []
    for line in src:
        dst.extend(bfrle_to_bfir(line))

    return dst

def bfrle_to_bfir(src: str, mode="auto") -> list[tuple[str, int]]:
    """mode: any of\n
        - prefix: prefix-only\n
        - suffix: suffix-only\n
        - auto: basically suffix. but if unused number is followed by command, treats it as prefix notation. "3>+2-" is ["3>", "+2", "-"]\n
    """
    dst = []
    if mode == "prefix":
        while len(src):
            m = re_bfrle_prefix_step.match(src)
            if not m:
                break

            n, c, rest = m.groups()
            if c in ("+", "-", ">", "<"):
                n = int(n) if n.isdigit() else 0
                dst.append((c, n))
            elif c in (",", ".", "[", "]", "[-]"):
                dst.append((c, 0))

            src = rest
    elif mode == "suffix":
        while len(src):
            m = re_bfrle_suffix_step.match(src)
            if not m:
                break

            c, n, rest = m.groups()
            if c in ("+", "-", ">", "<"):
                n = int(n) if n.isdigit() else 0
                dst.append((c, n))
            elif c in (",", ".", "[", "]", "[-]"):
                dst.append((c, 0))

            src = rest
    elif mode == "auto":
        while len(src):
            m = re_bfrle_step.match(src)
            if not m:
                break

            n, c, m, rest = m.groups()
            if c in ("+", "-", ">", "<"):
                if m != "":
                    m = int(m) if m.isdigit() else 0
                    dst.append((c, int(m)))
                    src = rest
                elif n != "":
                    n = int(n) if n.isdigit() else 0
                    dst.append((c, int(n)))
                    src = m + rest
            elif c in (",", ".", "[", "]", "[-]"):
                dst.append((c, 0))
                src = m + rest
            else:
                src = m + rest

    return dst
