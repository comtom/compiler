from compiler.exceptions import SymbolNotFound


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

        raise SymbolNotFound("Variable no definida '%s'" % sym)

    def set_sym(self, sym, val):
        self.__table[self.__sym][sym] = val
