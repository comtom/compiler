import sys
import types
import re
from compiler.lexer.lexer import Lexer
from compiler.lexer.lexer_reflect import LexerReflect
from compiler.lexer.logger import Logger


def _get_regex(func):
    return getattr(func, 'regex', func.__doc__)


def get_caller_module_dict(levels):
    f = sys._getframe(levels)
    ldict = f.f_globals.copy()
    if f.f_globals != f.f_locals:
        ldict.update(f.f_locals)
    return ldict


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


def build(module=None, object=None, lextab='lextab', reflags=int(re.VERBOSE), nowarn=False, outputdir=None, debuglog=None, errorlog=None):
    if lextab is None:
        lextab = 'lextab'

    global lexer
    ldict = None
    stateinfo = {'INITIAL': 'inclusive'}
    lexobj = Lexer()
    global token, input

    if errorlog is None:
        errorlog = Logger(sys.stderr)

    if object:
        module = object

    if module:
        _items = [(k, getattr(module, k)) for k in dir(module)]
        ldict = dict(_items)
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
        errorlog.warning('No se ha definido la regla: t_error')

    lexobj.lexstateeoff = linfo.eoff
    lexobj.lexeoff = linfo.eoff.get('INITIAL', None)

    for s, stype in stateinfo.items():
        if stype == 'exclusive':
            if s not in linfo.errorf:
                errorlog.warning("No se ha definido una regla de error para el estado '%s'", s)
            if s not in linfo.ignore and lexobj.lexignore:
                errorlog.warning("No se ha definido una regla para ignorar la entrada en el estado '%s'", s)
        elif stype == 'inclusive':
            if s not in linfo.errorf:
                linfo.errorf[s] = linfo.errorf.get('INITIAL', None)
            if s not in linfo.ignore:
                linfo.ignore[s] = linfo.ignore.get('INITIAL', '')

    token = lexobj.token
    input = lexobj.input
    lexer = lexobj

    return lexobj


def TOKEN(r):
    def set_regex(f):
        if hasattr(r, '__call__'):
            f.regex = _get_regex(r)
        else:
            f.regex = r
        return f

    return set_regex

Token = TOKEN
