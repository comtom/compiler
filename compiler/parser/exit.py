from compiler.parser import BaseExpression


class ExitStatement(BaseExpression):
    def __iter__(self):
        return []

    def eval(self):
        pass
