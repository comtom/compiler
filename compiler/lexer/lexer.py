import os
import sys
import re
import types
import copy
from compiler.exceptions import LexicalError
from compiler.lexer.token import AToken


StringTypes = (str, bytes)
_is_identifier = re.compile(r'^[a-zA-Z0-9_]+$')


class Lexer:
    def __init__(self):
        self.lexre = None           # expresion regular base
        self.lexretext = None       # regex para strings
        self.lexstatere = {}        # mapeo de estados del lexer a la regex base
        self.lexstateretext = {}    # mapeo de estados del lexer a la regex de strings
        self.lexstaterenames = {}   # mapeo de estados del lexer a nombres de simbolos
        self.lexstate = 'INITIAL'   # estado actual del lexer
        self.lexstatestack = []     # pila de estados del lexer
        self.lexstateinfo = None    # info del estado
        self.lexstateignore = {}    # dict de caracteres ignorados para cada estado
        self.lexstateerrorf = {}    # dict de funciones de error para cada estado
        self.lexstateeoff = {}      # dict para las funciones de fin de linea para cada estado
        self.lexreflags = 0         # flags para el modulo re
        self.lexdata = None         # informacion de entrada como string
        self.lexpos = 0             # posicion actual en el texto de entrada
        self.lexlen = 0             # largo del texto de entrada
        self.lexerrorf = None       # reglas de error
        self.lexeoff = None         # fin de linea
        self.lextokens = None       # lista de tokens validos
        self.lexignore = ''         # caracteres ignored
        self.lexliterals = ''       # Literal characters that can be passed through
        self.lexmodule = None       # modulo
        self.lineno = 1             # linea actual

    @staticmethod
    def funcs_to_names(funclist, namelist):
        result = []
        for f, name in zip(funclist, namelist):
            if f and f[0]:
                result.append((name, f[1]))
            else:
                result.append(f)
        return result

    @staticmethod
    def _names_to_funcs(namelist, fdict):
        result = []
        for n in namelist:
            if n and n[0]:
                result.append((fdict[n[0]], n[1]))
            else:
                result.append(n)
        return result

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
                    titem.append((retext, self.funcs_to_names(func, renames)))
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
                titem.append((re.compile(pat, lextab._lexreflags), self.names_to_funcs(func_name, fdict)))

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
            # hack para evitar problemas con los espacios, tabs y caracteres ingnorados
            if lexdata[lexpos] in lexignore:
                lexpos += 1
                continue

            # busca la regex
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
                    raise LexicalError("%s:%d: La regla '%s' retorno un token desconocido: '%s'" % (
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
                        raise LexicalError("Error: Caracter invalido: '%s'" % (lexdata[lexpos]), lexdata[lexpos:])
                    lexpos = self.lexpos
                    if not newtok:
                        continue
                    return newtok

                self.lexpos = lexpos
                raise LexicalError("Caracter invalido '%s' en posicion %d" % (lexdata[lexpos], lexpos), lexdata[lexpos:])

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
