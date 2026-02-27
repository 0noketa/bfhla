
# default configuration for bfhla

# general

# codegen
INDENT_UNIT = "    "
VERBOSE = True
MAX_LINE_COL = 80  # for non verbose output



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
        self.verbose: bool = VERBOSE
        self.max_line_col: int = MAX_LINE_COL

general = GeneralConfig()
codegen = CodegenConfig()

