
from typing import cast, Tuple
import re
import config.bfhla as bfhla_config
from bfhla.struct import *
import bf.parser as bf_parser


lex = re.compile("""\\s*(
    "(?:[^"]|\\")*"
    |[0-9]+
    |[a-zA-Z_][a-zA-Z0-9_]*
    |==
    |!=
    |>=
    |<=
    |\\->
    |<\\-
    |[+\\-*/%^&\\|@\\$\\?\\:!><,.\\[\\]\\{\\}\\(\\)=]
    |\\#
)""".replace(" ", "").replace("\n", "").replace("\r", ""))


class Lex:
    @staticmethod
    def lex_lines(ss: list[str]) -> tuple[tuple[str|tuple, ...], ...]:
        dst = []
        for s in ss:
            tkns = lex.findall(s)
            tkns = Lex.remove_comment(tkns)
            tkns, _ = Lex.fold_blocks(tkns)
            if tkns:
                dst.append(tkns)

        return tuple(dst)

    @staticmethod
    def remove_comment(tkns: list[str]) -> list[str]:
        if "#" in tkns:
            i = tkns.index("#")
            tkns = tkns[:i]

        return tkns
    @staticmethod
    def block_left_by_right(s: str) -> str:
        return {"(": ")", "[": "]", "{": "}"}[s]
    @staticmethod
    def fold_blocks(tkns: list[str], block_right="(") -> tuple[tuple[str|tuple, ...], int]:
        """last step. this method turns lists into tuples"""
        block_left = Lex.block_left_by_right(block_right)
        dst = []
        i = 0
        while i < len(tkns):
            tkn = tkns[i]

            if tkn in ("(", "[", "{"):
                block, j = Lex.fold_blocks(tkns[i + 1:], tkn)
                dst.append(block)
                i += j + 1
                continue
            elif tkn == block_left:
                return tuple(dst), i + 1
            elif tkn in (")", "]", "}"):
                return tuple(dst), i + 1

            dst.append(tkn)
            i += 1

        return tuple(dst), i
