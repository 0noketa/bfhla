
INDENT_UNIT = "    "
BUF_SIZE = 32767
GLOBAL_SCOPE_NAME = "mem"
NAMED_VARS = [chr(ord('a') + i) for i in range(26)]

KEEP_ALL_MOVE_DST = True    # does not remove "move x+0 = y"
MAX_INLINE_BF_LENGTH = 64    # merges inline BF until this length
NO_BFRLE = False    # disables BF-RLE(suffix) as inline BF
NO_SEMANTIC_ANALYSER = False    # outputs only raw loops
EXPLICIT_MOVE = False    # disables implicit assignment form
