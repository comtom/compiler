import operator
from types import LambdaType
from compiler.parser import BaseExpression
from compiler.parser.identifier import Identifier
from compiler.exceptions import CompilerRuntimeError


class BinaryOperation(BaseExpression):
    __operations = {
        '+': operator.add,
        '*': operator.mul,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
    }

    def __repr__(self):
        return '<BinaryOperation left ={0} right={1} operation="{2}">'.format(self.left, self.right, self.op)

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    def eval(self):
        left = None
        right = None

        try:
            op = self.__operations[self.op]

            if isinstance(op, LambdaType):
                return op(self.left, self.right)

            left = self.left.eval()
            right = self.right.eval()
            return op(left, right)
        except TypeError:
            fmt = (left.__class__.__name__, left, self.op, right.__class__.__name__, right)
            raise CompilerRuntimeError("Error: No se ha podido realizar la operacion (%s: %s) %s (%s: %s)" % fmt)


class Assignment(BaseExpression):
    def __init__(self, identifier: Identifier, val):
        self.identifier = identifier
        self.val = val

    def __repr__(self):
        return '<Assignment sym={0}; val={1}>'.format(self.identifier, self.val)

    def eval(self):
        self.identifier.assign(self.val.eval())
