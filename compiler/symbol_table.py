from exceptions import SymbolNotFound


class SymbolTable:
    __func = 'functions'
    __sym = 'symbols'
    __local = 'local'

    __table = {
        __func: {},
        __sym: {},
        __local: []
    }

    def __is_local(self):
        return len(self.__table[self.__local]) > 0

    def table(self):
        return self.__table

    def get_local_table(self):
        t = self.__table[self.__local]

        return t[len(t) - 1]

    def set_local(self, flag):
        if flag:
            self.__table[self.__local].append({})
        else:
            self.__table[self.__local].pop()

    def get_sym(self, sym):
        if self.__is_local():
            for tab in reversed(self.__table[self.__local]):
                if sym in tab:
                    return tab[sym]

        # if not found check the global scope
        if sym in self.__table[self.__sym]:
            return self.__table[self.__sym][sym]

        raise SymbolNotFound("Variable no definida '%s'" % sym)

    def set_sym(self, sym, val):
        if self.__is_local():
            self.get_local_table()[sym] = val
        else:
            self.__table[self.__sym][sym] = val
