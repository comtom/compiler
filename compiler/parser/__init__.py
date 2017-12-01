from compiler import symbol_table


symbols = symbol_table.SymbolTable()


class BaseExpression:
    def eval(self):
        raise NotImplementedError()


class InstructionList:
    def __init__(self, children=None):
        if children is None:
            children = []
        self.children = children

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __repr__(self):
        return '<InstructionList {0}>'.format(self.children)

    def eval(self):
        ret = []
        for n in self:
            res = n.eval()

            if res is not None:
                ret.append(res)

        return ret


class Primitive(BaseExpression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<Primitive "{0}"({1})>'.format(self.value, self.value.__class__)

    def eval(self):
        return self.value


def full_eval(expr: BaseExpression):
    while isinstance(expr, BaseExpression):
        expr = expr.eval()

    return expr
