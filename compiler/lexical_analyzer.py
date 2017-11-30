from compiler import lexer as lexer_module
from compiler.exceptions import UnexpectedChar


reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'print': 'PRINT',
    'integer': 'NUM_INT',
    'longint': 'NUM_LONG',
}

tokens = [
    'STMT_END',
    'EQUALS',
    'IDENTIFIER',
    'LPAREN',
    'RPAREN',
    'LBRACK',
    'RBRACK',
    'STRING',
    'NUM_INTEGER',
    'NUM_LONGINTEGER',
    'COMMA',
    'NEWLINE',
    'PLUS',
    'MINUS',
    'MUL',
    'EQ',
    'NEQ',
    'GT',
    'GTE',
    'LT',
    'LTE',
] + list(reserved.values())

t_COMMA = ','
t_PLUS = r'\+'
t_MINUS = '-'
t_MUL = r'\*'
t_STMT_END = ';'
t_EQUALS = ':='
t_ignore_WS = r'\s+'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACK = '{'
t_RBRACK = '}'
t_EQ = '='
t_NEQ = '!='
t_GT = '>'
t_GTE = '>='
t_LT = '<'
t_LTE = '<='
t_ignore_COMMENTS = r'&&.+'


def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    t.lexer.linepos = 0

    pass


def t_IDENTIFIER(t):
    r'[\$a-zA-Z]\w*'
    t.type = reserved.get(t.value, t.type)

    return t


def t_NUM_INTEGER(t):
    r'_i(\d+)'
    t.value = int(t.value[-2:])

    if t.value > 32767 or t.value < -32768:
        raise Exception('Constante entera fuera de rango en linea %s' % t.lexer.lineno)

    return t


def t_NUM_LONGINTEGER(t):
    r'_l(\d+)'
    t.value = int(t.value[-2:])

    if t.value > 4294967295 or t.value < -4294967296:
        raise Exception('Constante long fuera de rango en linea %s' % t.lexer.lineno)

    return t


def t_STRING(t):
    r'"(?:\\"|\+\n|.)*?"'
    t.value = bytes(t.value.replace('+\n', ' ').lstrip('"').rstrip('"'), "utf-8").decode("unicode_escape")

    return t


def t_error(t):
    raise UnexpectedChar("Caracter inesperado '%s' en linea %d" % (t.value[0], t.lineno))


def setup(source_file):
    lexer.input(str(source_file))
    return lexer


lexer = lexer_module.build()
