import json
from compiler.exceptions import SymbolNotFound
from compiler import errors


class SymbolTable:
    __sym = 'symbols'

    __table = {
        __sym: {},
    }

    def table(self):
        return self.__table

    def get_sym(self, sym):
        if sym in self.__table[self.__sym]:
            return self.__table[self.__sym][sym]

        errors.append("Error: Variable no definida '%s'" % sym)

    def set_sym(self, sym, val):
        self.__table[self.__sym][sym] = val

    def __repr__(self):
        return json.dumps(self.table())
