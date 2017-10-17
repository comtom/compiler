from compiler.parser import BaseExpression, InstructionList


class PrintStatement(BaseExpression):
    def __init__(self, items: InstructionList):
        self.items = items

    def __repr__(self):
        return '<Print {0}>'.format(self.items)

    def eval(self):
        print(*self.items.eval(), end='', sep='')
