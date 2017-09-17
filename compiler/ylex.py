import re
import sys
import types
import copy
import os
import inspect

from compiler.exceptions import LexError


StringTypes = (str, bytes)
_is_identifier = re.compile(r'^[a-zA-Z0-9_]+$')


class AToken:
    def __str__(self):
        return 'Token(%s,%r,%d,%d)' % (self.type, self.value, self.lineno, self.lexpos)

    def __repr__(self):
        return str(self)


class PlyLogger:
    def __init__(self, f):
        self.f = f

    def critical(self, msg, *args, **kwargs):
        self.f.write((msg % args) + '\n')

    def warning(self, msg, *args, **kwargs):
        self.f.write('WARNING: ' + (msg % args) + '\n')

    def error(self, msg, *args, **kwargs):
        self.f.write('ERROR: ' + (msg % args) + '\n')

    info = critical
    debug = critical


class NullLogger:
    def __getattribute__(self, name):
        return self

    def __call__(self, *args, **kwargs):
        return self


class Lexer:
    def __init__(self):
        self.lexre = None  # Master regular expression
        self.lexretext = None  # Current regular expression strings
        self.lexstatere = {}  # Dictionary mapping lexer states to master regexs
        self.lexstateretext = {}  # Dictionary mapping lexer states to regex strings
        self.lexstaterenames = {}  # Dictionary mapping lexer states to symbol names
        self.lexstate = 'INITIAL'  # Current lexer state
        self.lexstatestack = []  # Stack of lexer states
        self.lexstateinfo = None  # State information
        self.lexstateignore = {}  # Dictionary of ignored characters for each state
        self.lexstateerrorf = {}  # Dictionary of error functions for each state
        self.lexstateeoff = {}  # Dictionary of eof functions for each state
        self.lexreflags = 0  # Optional re compile flags
        self.lexdata = None  # Actual input data (as a string)
        self.lexpos = 0  # Current position in input text
        self.lexlen = 0  # Length of the input text
        self.lexerrorf = None  # Error rule (if any)
        self.lexeoff = None  # EOF rule (if any)
        self.lextokens = None  # List of valid tokens
        self.lexignore = ''  # Ignored characters
        self.lexliterals = ''  # Literal characters that can be passed through
        self.lexmodule = None  # Module
        self.lineno = 1  # Current line number

    def clone(self, object=None):
        c = copy.copy(self)

        if object:
            newtab = {}
            for key, ritem in self.lexstatere.items():
                newre = []
                for cre, findex in ritem:
                    newfindex = []
                    for f in findex:
                        if not f or not f[0]:
                            newfindex.append(f)
                            continue
                        newfindex.append((getattr(object, f[0].__name__), f[1]))
                newre.append((cre, newfindex))
                newtab[key] = newre
            c.lexstatere = newtab
            c.lexstateerrorf = {}
            for key, ef in self.lexstateerrorf.items():
                c.lexstateerrorf[key] = getattr(object, ef.__name__)
            c.lexmodule = object
        return c

    def writetab(self, lextab, outputdir=''):
        if isinstance(lextab, types.ModuleType):
            raise IOError("No sobreescribira el modulo")
        basetabmodule = lextab.split('.')[-1]
        filename = os.path.join(outputdir, basetabmodule) + '.py'
        with open(filename, 'w') as tf:
            tf.write('# %s.py. This file automatically created by PLY. Don\'t edit!\n' % basetabmodule)
            tf.write('_lextokens    = set(%s)\n' % repr(tuple(self.lextokens)))
            tf.write('_lexreflags   = %s\n' % repr(self.lexreflags))
            tf.write('_lexliterals  = %s\n' % repr(self.lexliterals))
            tf.write('_lexstateinfo = %s\n' % repr(self.lexstateinfo))
            tabre = {}
            for statename, lre in self.lexstatere.items():
                titem = []
                for (pat, func), retext, renames in zip(lre, self.lexstateretext[statename],
                                                        self.lexstaterenames[statename]):
                    titem.append((retext, _funcs_to_names(func, renames)))
                tabre[statename] = titem

            tf.write('_lexstatere   = %s\n' % repr(tabre))
            tf.write('_lexstateignore = %s\n' % repr(self.lexstateignore))

            taberr = {}
            for statename, ef in self.lexstateerrorf.items():
                taberr[statename] = ef.__name__ if ef else None
            tf.write('_lexstateerrorf = %s\n' % repr(taberr))

            tabeof = {}
            for statename, ef in self.lexstateeoff.items():
                tabeof[statename] = ef.__name__ if ef else None
            tf.write('_lexstateeoff = %s\n' % repr(tabeof))

    def readtab(self, tabfile, fdict):
        if isinstance(tabfile, types.ModuleType):
            lextab = tabfile
        else:
            exec('import %s' % tabfile)
            lextab = sys.modules[tabfile]

        self.lextokens = lextab._lextokens
        self.lexreflags = lextab._lexreflags
        self.lexliterals = lextab._lexliterals
        self.lextokens_all = self.lextokens | set(self.lexliterals)
        self.lexstateinfo = lextab._lexstateinfo
        self.lexstateignore = lextab._lexstateignore
        self.lexstatere = {}
        self.lexstateretext = {}
        for statename, lre in lextab._lexstatere.items():
            titem = []
            txtitem = []
            for pat, func_name in lre:
                titem.append((re.compile(pat, lextab._lexreflags), _names_to_funcs(func_name, fdict)))

            self.lexstatere[statename] = titem
            self.lexstateretext[statename] = txtitem

        self.lexstateerrorf = {}
        for statename, ef in lextab._lexstateerrorf.items():
            self.lexstateerrorf[statename] = fdict[ef]

        self.lexstateeoff = {}
        for statename, ef in lextab._lexstateeoff.items():
            self.lexstateeoff[statename] = fdict[ef]

        self.begin('INITIAL')

    def input(self, s):
        c = s[:1]
        if not isinstance(c, StringTypes):
            raise ValueError('Se esperaba un string')
        self.lexdata = s
        self.lexpos = 0
        self.lexlen = len(s)

    def begin(self, state):
        if state not in self.lexstatere:
            raise ValueError('Estado no definido')
        self.lexre = self.lexstatere[state]
        self.lexretext = self.lexstateretext[state]
        self.lexignore = self.lexstateignore.get(state, '')
        self.lexerrorf = self.lexstateerrorf.get(state, None)
        self.lexeoff = self.lexstateeoff.get(state, None)
        self.lexstate = state

    def push_state(self, state):
        self.lexstatestack.append(self.lexstate)
        self.begin(state)

    def pop_state(self):
        self.begin(self.lexstatestack.pop())

    def current_state(self):
        return self.lexstate

    def skip(self, n):
        self.lexpos += n

    def token(self):
        lexpos = self.lexpos
        lexlen = self.lexlen
        lexignore = self.lexignore
        lexdata = self.lexdata

        while lexpos < lexlen:
            # p/ evitar problemas con los espacios, tabs y caracteres ingnorados
            if lexdata[lexpos] in lexignore:
                lexpos += 1
                continue

            # Look for a regular expression match
            for lexre, lexindexfunc in self.lexre:
                m = lexre.match(lexdata, lexpos)
                if not m:
                    continue

                tok = AToken()
                tok.value = m.group()
                tok.lineno = self.lineno
                tok.lexpos = lexpos
                i = m.lastindex
                func, tok.type = lexindexfunc[i]

                if not func:
                    if tok.type:
                        self.lexpos = m.end()
                        return tok
                    else:
                        lexpos = m.end()
                        break

                lexpos = m.end()
                tok.lexer = self
                self.lexmatch = m
                self.lexpos = lexpos
                newtok = func(tok)

                if not newtok:
                    lexpos = self.lexpos
                    lexignore = self.lexignore
                    break

                if newtok.type not in self.lextokens_all:
                    raise LexError("%s:%d: La regla '%s' retorno un token desconocido: '%s'" % (
                        func.__code__.co_filename, func.__code__.co_firstlineno,
                        func.__name__, newtok.type), lexdata[lexpos:])

                return newtok
            else:
                if lexdata[lexpos] in self.lexliterals:
                    tok = AToken()
                    tok.value = lexdata[lexpos]
                    tok.lineno = self.lineno
                    tok.type = tok.value
                    tok.lexpos = lexpos
                    self.lexpos = lexpos + 1
                    return tok

                if self.lexerrorf:
                    tok = AToken()
                    tok.value = self.lexdata[lexpos:]
                    tok.lineno = self.lineno
                    tok.type = 'error'
                    tok.lexer = self
                    tok.lexpos = lexpos
                    self.lexpos = lexpos
                    newtok = self.lexerrorf(tok)
                    if lexpos == self.lexpos:
                        # Error method didn't change text position at all. This is an error.
                        raise LexError("Error: Caracter invalido: '%s'" % (lexdata[lexpos]), lexdata[lexpos:])
                    lexpos = self.lexpos
                    if not newtok:
                        continue
                    return newtok

                self.lexpos = lexpos
                raise LexError("Caracter invalido '%s' en posicion %d" % (lexdata[lexpos], lexpos), lexdata[lexpos:])

        if self.lexeoff:
            tok = AToken()
            tok.type = 'eof'
            tok.value = ''
            tok.lineno = self.lineno
            tok.lexpos = lexpos
            tok.lexer = self
            self.lexpos = lexpos
            newtok = self.lexeoff(tok)
            return newtok

        self.lexpos = lexpos + 1
        if self.lexdata is None:
            raise RuntimeError('No se especifico un string al llamar a input()')
        return None

    def __iter__(self):
        return self

    def next(self):
        t = self.token()
        if t is None:
            raise StopIteration
        return t

    __next__ = next



def _get_regex(func):
    return getattr(func, 'regex', func.__doc__)


def get_caller_module_dict(levels):
    f = sys._getframe(levels)
    ldict = f.f_globals.copy()
    if f.f_globals != f.f_locals:
        ldict.update(f.f_locals)
    return ldict


def _funcs_to_names(funclist, namelist):
    result = []
    for f, name in zip(funclist, namelist):
        if f and f[0]:
            result.append((name, f[1]))
        else:
            result.append(f)
    return result


def _names_to_funcs(namelist, fdict):
    result = []
    for n in namelist:
        if n and n[0]:
            result.append((fdict[n[0]], n[1]))
        else:
            result.append(n)
    return result


def _form_master_re(relist, reflags, ldict, toknames):
    if not relist:
        return []
    regex = '|'.join(relist)
    try:
        lexre = re.compile(regex, reflags)
        lexindexfunc = [None] * (max(lexre.groupindex.values()) + 1)
        lexindexnames = lexindexfunc[:]

        for f, i in lexre.groupindex.items():
            handle = ldict.get(f, None)
            if type(handle) in (types.FunctionType, types.MethodType):
                lexindexfunc[i] = (handle, toknames[f])
                lexindexnames[i] = f
            elif handle is not None:
                lexindexnames[i] = f
                if f.find('ignore_') > 0:
                    lexindexfunc[i] = (None, None)
                else:
                    lexindexfunc[i] = (None, toknames[f])

        return [(lexre, lexindexfunc)], [regex], [lexindexnames]
    except Exception:
        m = int(len(relist) / 2)
        if m == 0:
            m = 1
        llist, lre, lnames = _form_master_re(relist[:m], reflags, ldict, toknames)
        rlist, rre, rnames = _form_master_re(relist[m:], reflags, ldict, toknames)
        return (llist + rlist), (lre + rre), (lnames + rnames)


def _statetoken(s, names):
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


class LexerReflect(object):
    def __init__(self, ldict, log=None, reflags=0):
        self.ldict = ldict
        self.error_func = None
        self.tokens = []
        self.reflags = reflags
        self.stateinfo = {'INITIAL': 'inclusive'}
        self.modules = set()
        self.error = False
        self.log = PlyLogger(sys.stderr) if log is None else log

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
            states, tokname = _statetoken(f, self.stateinfo)
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
                    self.log.error("%s:%d: Rule '%s' must be defined as a string", file, line, t.__name__)
                    self.error = True
                else:
                    for s in states:
                        self.funcsym[s].append((f, t))
            elif isinstance(t, StringTypes):
                if tokname == 'ignore':
                    for s in states:
                        self.ignore[s] = t
                    if '\\' in t:
                        self.log.warning("%s contains a literal backslash '\\'", f)

                elif tokname == 'error':
                    self.log.error("Rule '%s' must be defined as a function", f)
                    self.error = True
                else:
                    for s in states:
                        self.strsym[s].append((f, t))
            else:
                self.log.error('%s not defined as a function or string', f)
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
                    self.log.error("%s:%d: Rule '%s' has too many arguments", file, line, f.__name__)
                    self.error = True
                    continue

                if nargs < reqargs:
                    self.log.error("%s:%d: Rule '%s' requires an argument", file, line, f.__name__)
                    self.error = True
                    continue

                if not _get_regex(f):
                    self.log.error("%s:%d: No regular expression defined for rule '%s'", file, line, f.__name__)
                    self.error = True
                    continue

                try:
                    c = re.compile('(?P<%s>%s)' % (fname, _get_regex(f)), self.reflags)
                    if c.match(''):
                        self.log.error("%s:%d: Regular expression for rule '%s' matches empty string", file, line,
                                       f.__name__)
                        self.error = True
                except re.error as e:
                    self.log.error("%s:%d: Invalid regular expression for rule '%s'. %s", file, line, f.__name__, e)
                    if '#' in _get_regex(f):
                        self.log.error("%s:%d. Make sure '#' in rule '%s' is escaped with '\\#'", file, line,
                                       f.__name__)
                    self.error = True

            for name, r in self.strsym[state]:
                tokname = self.toknames[name]
                if tokname == 'error':
                    self.log.error("Rule '%s' must be defined as a function", name)
                    self.error = True
                    continue

                if tokname not in self.tokens and tokname.find('ignore_') < 0:
                    self.log.error("Rule '%s' defined for an unspecified token %s", name, tokname)
                    self.error = True
                    continue

                try:
                    c = re.compile('(?P<%s>%s)' % (name, r), self.reflags)
                    if (c.match('')):
                        self.log.error("Regular expression for rule '%s' matches empty string", name)
                        self.error = True
                except re.error as e:
                    self.log.error("Invalid regular expression for rule '%s'. %s", name, e)
                    if '#' in r:
                        self.log.error("Make sure '#' in rule '%s' is escaped with '\\#'", name)
                    self.error = True

            if not self.funcsym[state] and not self.strsym[state]:
                self.log.error("No rules defined for state '%s'", state)
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
                    self.log.error("%s:%d: Rule '%s' has too many arguments", file, line, f.__name__)
                    self.error = True

                if nargs < reqargs:
                    self.log.error("%s:%d: Rule '%s' requires an argument", file, line, f.__name__)
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
                    self.log.error('%s:%d: Rule %s redefined. Previously defined on line %d', filename, linen, name,
                                   prev)
                    self.error = True
            linen += 1


def lex(module=None, object=None, lextab='lextab', reflags=int(re.VERBOSE), nowarn=False, outputdir=None, debuglog=None, errorlog=None):
    if lextab is None:
        lextab = 'lextab'

    global lexer
    ldict = None
    stateinfo = {'INITIAL': 'inclusive'}
    lexobj = Lexer()
    global token, input

    if errorlog is None:
        errorlog = PlyLogger(sys.stderr)

    if object:
        module = object

    if module:
        _items = [(k, getattr(module, k)) for k in dir(module)]
        ldict = dict(_items)
        # If no __file__ attribute is available, try to obtain it from the __module__ instead
        if '__file__' not in ldict:
            ldict['__file__'] = sys.modules[ldict['__module__']].__file__
    else:
        ldict = get_caller_module_dict(2)

    pkg = ldict.get('__package__')
    if pkg and isinstance(lextab, str):
        if '.' not in lextab:
            lextab = pkg + '.' + lextab

    linfo = LexerReflect(ldict, log=errorlog, reflags=reflags)
    linfo.get_all()

    if linfo.validate_all():
        raise SyntaxError("Error de validacion. No se puede construir el parser")

    lexobj.lextokens = set()
    for n in linfo.tokens:
        lexobj.lextokens.add(n)

    if isinstance(linfo.literals, (list, tuple)):
        lexobj.lexliterals = type(linfo.literals[0])().join(linfo.literals)
    else:
        lexobj.lexliterals = linfo.literals

    lexobj.lextokens_all = lexobj.lextokens | set(lexobj.lexliterals)

    stateinfo = linfo.stateinfo

    regexs = {}
    for state in stateinfo:
        regex_list = []

        for fname, f in linfo.funcsym[state]:
            regex_list.append('(?P<%s>%s)' % (fname, _get_regex(f)))

        for name, r in linfo.strsym[state]:
            regex_list.append('(?P<%s>%s)' % (name, r))

        regexs[state] = regex_list

    for state in regexs:
        lexre, re_text, re_names = _form_master_re(regexs[state], reflags, ldict, linfo.toknames)
        lexobj.lexstatere[state] = lexre
        lexobj.lexstateretext[state] = re_text
        lexobj.lexstaterenames[state] = re_names

    for state, stype in stateinfo.items():
        if state != 'INITIAL' and stype == 'inclusive':
            lexobj.lexstatere[state].extend(lexobj.lexstatere['INITIAL'])
            lexobj.lexstateretext[state].extend(lexobj.lexstateretext['INITIAL'])
            lexobj.lexstaterenames[state].extend(lexobj.lexstaterenames['INITIAL'])

    lexobj.lexstateinfo = stateinfo
    lexobj.lexre = lexobj.lexstatere['INITIAL']
    lexobj.lexretext = lexobj.lexstateretext['INITIAL']
    lexobj.lexreflags = reflags

    lexobj.lexstateignore = linfo.ignore
    lexobj.lexignore = lexobj.lexstateignore.get('INITIAL', '')

    lexobj.lexstateerrorf = linfo.errorf
    lexobj.lexerrorf = linfo.errorf.get('INITIAL', None)
    if not lexobj.lexerrorf:
        errorlog.warning('No t_error rule is defined')

    lexobj.lexstateeoff = linfo.eoff
    lexobj.lexeoff = linfo.eoff.get('INITIAL', None)

    for s, stype in stateinfo.items():
        if stype == 'exclusive':
            if s not in linfo.errorf:
                errorlog.warning("No error rule is defined for exclusive state '%s'", s)
            if s not in linfo.ignore and lexobj.lexignore:
                errorlog.warning("No ignore rule is defined for exclusive state '%s'", s)
        elif stype == 'inclusive':
            if s not in linfo.errorf:
                linfo.errorf[s] = linfo.errorf.get('INITIAL', None)
            if s not in linfo.ignore:
                linfo.ignore[s] = linfo.ignore.get('INITIAL', '')

    token = lexobj.token
    input = lexobj.input
    lexer = lexobj

    return lexobj


def runmain(lexer=None, data=None):
    if not data:
        try:
            filename = sys.argv[1]
            f = open(filename)
            data = f.read()
            f.close()
        except IndexError:
            sys.stdout.write('Reading from standard input (type EOF to end):\n')
            data = sys.stdin.read()

    if lexer:
        _input = lexer.input
    else:
        _input = input
    _input(data)
    if lexer:
        _token = lexer.token
    else:
        _token = token

    while True:
        tok = _token()
        if not tok:
            break
        sys.stdout.write('(%s,%r,%d,%d)\n' % (tok.type, tok.value, tok.lineno, tok.lexpos))


def TOKEN(r):
    def set_regex(f):
        if hasattr(r, '__call__'):
            f.regex = _get_regex(r)
        else:
            f.regex = r
        return f

    return set_regex

Token = TOKEN
