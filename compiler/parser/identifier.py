from compiler.parser import BaseExpression, symbols



class Identifier(BaseExpression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Identifier {0}>'.format(self.name)

    def assign(self, val):
        symbols.set_sym(self.name, val)

    def eval(self):
        return symbols.get_sym(self.name)
