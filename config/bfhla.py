
# default configuration for bfhla

# general
NO_SEMANTIC_ANALYSER = False    # outputs only raw loops

# codegen
INDENT_UNIT = "    "
MAX_INLINE_BF_LENGTH = 64    # merges inline BF until this length
NO_BFRLE = False    # disables BF-RLE(suffix) as inline BF

# disasm
BUF_SIZE = 32767
GLOBAL_SCOPE_NAME = "mem"
NAMED_VARS = [chr(ord('a') + i) for i in range(26)]
EXPLICIT_MOVE = False    # disables implicit assignment form



class Config:
    def init_all(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    def replace(self, key, value):
        setattr(self, key, value)

class GeneralConfig(Config):
    def __init__(self, **kwargs):
        super().__init__()
        self.no_semantic_analyser: bool = NO_SEMANTIC_ANALYSER
class CodegenConfig(Config):
    def __init__(self, **kwargs):
        super().__init__()
        self.indent_unit: str = INDENT_UNIT
        self.max_inline_bf_length: int = MAX_INLINE_BF_LENGTH
        self.no_bfrle: bool = NO_BFRLE
        self.explicit_move: bool = EXPLICIT_MOVE
class DisasmConfig(Config):
    def __init__(self, **kwargs):
        super().__init__()
        self.buf_size: int = BUF_SIZE
        self.global_scope_name: str = GLOBAL_SCOPE_NAME
        self.named_vars: list[str] = NAMED_VARS

general = GeneralConfig()
codegen = CodegenConfig()
disasm = DisasmConfig()

