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


class IdentifierList(BaseExpression):
    def __init__(self, children=None):
        if children is None:
            children = []
        self.children = children

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __repr__(self):
        return '<IdentifierList {0}>'.format(self.children)

    def eval(self):
        ret = []
        for n in self:
            res = n.eval()

            if res is not None:
                ret.append(res)

        return ret
