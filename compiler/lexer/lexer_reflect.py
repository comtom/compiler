import inspect
from compiler.lexer import *
from compiler.lexer.lexer import StringTypes, _is_identifier
from compiler.lexer.logger import Logger


class LexerReflect(object):
    def __init__(self, ldict, log=None, reflags=0):
        self.ldict = ldict
        self.error_func = None
        self.tokens = []
        self.reflags = reflags
        self.stateinfo = {'INITIAL': 'inclusive'}
        self.modules = set()
        self.error = False
        self.log = Logger(sys.stderr) if log is None else log

    @staticmethod
    def get_regex(func):
        return getattr(func, 'regex', func.__doc__)

    @staticmethod
    def statetoken(s, names):
        parts = s.split('_')
        for i, part in enumerate(parts[1:], 1):
            if part not in names and part != 'ANY':
                break

        if i > 1:
            states = tuple(parts[1:i])
        else:
            states = ('INITIAL',)

        if 'ANY' in states:
            states = tuple(names)

        tokenname = '_'.join(parts[i:])
        return (states, tokenname)

    def get_all(self):
        self.get_tokens()
        self.get_literals()
        self.get_states()
        self.get_rules()

    def validate_all(self):
        self.validate_tokens()
        self.validate_literals()
        self.validate_rules()
        return self.error

    def get_tokens(self):
        tokens = self.ldict.get('tokens', None)
        if not tokens:
            self.log.error('Ningun token ha sido definido')
            self.error = True
            return

        if not isinstance(tokens, (list, tuple)):
            self.log.error('La definicion de tokens debe ser una lista o tupla')
            self.error = True
            return

        if not tokens:
            self.log.error('La definicion de tokens esta vacia')
            self.error = True
            return

        self.tokens = tokens

    def validate_tokens(self):
        terminals = {}
        for n in self.tokens:
            if not _is_identifier.match(n):
                self.log.error("Nombre de token invalido: '%s'", n)
                self.error = True
            if n in terminals:
                self.log.warning("El token '%s' esta definido varias veces", n)
            terminals[n] = 1

    def get_literals(self):
        self.literals = self.ldict.get('literals', '')
        if not self.literals:
            self.literals = ''

    def validate_literals(self):
        try:
            for c in self.literals:
                if not isinstance(c, StringTypes) or len(c) > 1:
                    self.log.error('Literal invalido %s. Debe ser un solo caracter', repr(c))
                    self.error = True

        except TypeError:
            self.log.error('Especificacion de literales invalida. Deben ser una secuencia de caracteres')
            self.error = True

    def get_states(self):
        self.states = self.ldict.get('states', None)
        # Build statemap
        if self.states:
            if not isinstance(self.states, (tuple, list)):
                self.log.error('los estados deben ser definidos como una lista o tupla')
                self.error = True
            else:
                for s in self.states:
                    if not isinstance(s, tuple) or len(s) != 2:
                        self.log.error("Especificacion de estado invalida %s. Debe ser una tupla (statename,'exclusive|inclusive')",
                                       repr(s))
                        self.error = True
                        continue
                    name, statetype = s
                    if not isinstance(name, StringTypes):
                        self.log.error('Nombre de estaod %s debe ser un string', repr(name))
                        self.error = True
                        continue
                    if not (statetype == 'inclusive' or statetype == 'exclusive'):
                        self.log.error("El tipo de estado %s debe ser 'inclusive' o 'exclusive'", name)
                        self.error = True
                        continue
                    if name in self.stateinfo:
                        self.log.error("Estado '%s' ya definido", name)
                        self.error = True
                        continue
                    self.stateinfo[name] = statetype

    def get_rules(self):
        tsymbols = [f for f in self.ldict if f[:2] == 't_']

        # Now build up a list of functions and a list of strings
        self.toknames = {}  # Mapping of symbols to token names
        self.funcsym = {}  # Symbols defined as functions
        self.strsym = {}  # Symbols defined as strings
        self.ignore = {}  # Ignore strings by state
        self.errorf = {}  # Error functions by state
        self.eoff = {}  # EOF functions by state

        for s in self.stateinfo:
            self.funcsym[s] = []
            self.strsym[s] = []

        if len(tsymbols) == 0:
            self.log.error('No hay reglas de la forma t_rulename definidas')
            self.error = True
            return

        for f in tsymbols:
            t = self.ldict[f]
            states, tokname = self.statetoken(f, self.stateinfo)
            self.toknames[f] = tokname

            if hasattr(t, '__call__'):
                if tokname == 'error':
                    for s in states:
                        self.errorf[s] = t
                elif tokname == 'eof':
                    for s in states:
                        self.eoff[s] = t
                elif tokname == 'ignore':
                    line = t.__code__.co_firstlineno
                    file = t.__code__.co_filename
                    self.log.error("%s:%d: La regla '%s' debe ser definida como un string", file, line, t.__name__)
                    self.error = True
                else:
                    for s in states:
                        self.funcsym[s].append((f, t))
            elif isinstance(t, StringTypes):
                if tokname == 'ignore':
                    for s in states:
                        self.ignore[s] = t
                    if '\\' in t:
                        self.log.warning("%s contiene una barra '\\'", f)

                elif tokname == 'error':
                    self.log.error("Rule '%s' debe ser definida como una funcion", f)
                    self.error = True
                else:
                    for s in states:
                        self.strsym[s].append((f, t))
            else:
                self.log.error('%s no definida como una funcion o un string', f)
                self.error = True

        for f in self.funcsym.values():
            f.sort(key=lambda x: x[1].__code__.co_firstlineno)

        for s in self.strsym.values():
            s.sort(key=lambda x: len(x[1]), reverse=True)

    def validate_rules(self):
        for state in self.stateinfo:
            for fname, f in self.funcsym[state]:
                line = f.__code__.co_firstlineno
                file = f.__code__.co_filename
                module = inspect.getmodule(f)
                self.modules.add(module)

                tokname = self.toknames[fname]
                if isinstance(f, types.MethodType):
                    reqargs = 2
                else:
                    reqargs = 1
                nargs = f.__code__.co_argcount
                if nargs > reqargs:
                    self.log.error("%s:%d: La regla '%s' posee demasiados argumentos", file, line, f.__name__)
                    self.error = True
                    continue

                if nargs < reqargs:
                    self.log.error("%s:%d: La regla '%s' require al menos un argumento", file, line, f.__name__)
                    self.error = True
                    continue

                if not self.get_regex(f):
                    self.log.error("%s:%d: No ha definido una expresion regular para la regla '%s'", file, line, f.__name__)
                    self.error = True
                    continue

                try:
                    c = re.compile('(?P<%s>%s)' % (fname, self.get_regex(f)), self.reflags)
                    if c.match(''):
                        self.log.error("%s:%d: La expresion regular para la regla '%s' coincide para un string vacio", file, line,
                                       f.__name__)
                        self.error = True
                except re.error as e:
                    self.log.error("%s:%d: Expresion regular invalida para la regla '%s'. %s", file, line, f.__name__, e)
                    if '#' in self.get_regex(f):
                        self.log.error("%s:%d. El caracter '#' no ha siddo escapado en '%s' debe escaparlo con '\\#'", file, line,
                                       f.__name__)
                    self.error = True

            for name, r in self.strsym[state]:
                tokname = self.toknames[name]
                if tokname == 'error':
                    self.log.error("La regla '%s' debe ser definida como una funcion", name)
                    self.error = True
                    continue

                if tokname not in self.tokens and tokname.find('ignore_') < 0:
                    self.log.error("La regla '%s' esta definida para un token no especificado %s", name, tokname)
                    self.error = True
                    continue

                try:
                    c = re.compile('(?P<%s>%s)' % (name, r), self.reflags)
                    if (c.match('')):
                        self.log.error("La expresion regular para la regla '%s' coincide para un string vacio", name)
                        self.error = True
                except re.error as e:
                    self.log.error("La expresion regular es invalida para la regla '%s'. %s", name, e)
                    if '#' in r:
                        self.log.error("%s:%d. El caracter '#' no ha sido escapado en '%s' debe escaparlo con '\\#'", name)
                    self.error = True

            if not self.funcsym[state] and not self.strsym[state]:
                self.log.error("No hay reglas definidas para el estado '%s'", state)
                self.error = True

            efunc = self.errorf.get(state, None)
            if efunc:
                f = efunc
                line = f.__code__.co_firstlineno
                file = f.__code__.co_filename
                module = inspect.getmodule(f)
                self.modules.add(module)

                if isinstance(f, types.MethodType):
                    reqargs = 2
                else:
                    reqargs = 1
                nargs = f.__code__.co_argcount
                if nargs > reqargs:
                    self.log.error("%s:%d: La regla '%s' posee demasiados argumentos", file, line, f.__name__)
                    self.error = True

                if nargs < reqargs:
                    self.log.error("%s:%d: La regla '%s' require al menos un argumento", file, line, f.__name__)
                    self.error = True

        for module in self.modules:
            self.validate_module(module)


    def validate_module(self, module):
        try:
            lines, linen = inspect.getsourcelines(module)
        except IOError:
            return

        fre = re.compile(r'\s*def\s+(t_[a-zA-Z_0-9]*)\(')
        sre = re.compile(r'\s*(t_[a-zA-Z_0-9]*)\s*=')

        counthash = {}
        linen += 1
        for line in lines:
            m = fre.match(line)
            if not m:
                m = sre.match(line)
            if m:
                name = m.group(1)
                prev = counthash.get(name)
                if not prev:
                    counthash[name] = linen
                else:
                    filename = inspect.getsourcefile(module)
                    self.log.error('%s:%d: La regla %s fue previamente definida en la linea %d', filename, linen, name,
                                   prev)
                    self.error = True
            linen += 1
