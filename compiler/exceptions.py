class CompilerError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class LexicalError(CompilerError):
    def __init__(self, message, s):
        self.args = (message,)
        self.text = s


class ParserSyntaxError(CompilerError):
    pass


class SymbolNotFound(CompilerError):
    pass


class UnexpectedChar(CompilerError):
    pass


class CompilerRuntimeError(CompilerError):
    pass
