
# default configuration for bfhla

# general

# codegen
INDENT_UNIT = "    "
CELL_TYPE = "uint8_t"
BUF_SIZE = 32767
BUF_NAME = "bf_mem"
NAMED_VARS = [chr(ord('a') + i) for i in range(26)]



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
class CodegenConfig(Config):
    def __init__(self, **kwargs):
        super().__init__()
        self.indent_unit: str = INDENT_UNIT
        self.cell_type: str = CELL_TYPE
        self.buf_size: int = BUF_SIZE
        self.buf_name: str = BUF_NAME
        self.named_vars: list[str] = NAMED_VARS

general = GeneralConfig()
codegen = CodegenConfig()

