"""Module that implements a lexical analyzer."""
import compiler.ylex as lexical_analyzer
from compiler.exceptions import *


reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'endif': 'ENDIF',

    'while': 'WHILE',

    'print': 'PRINT',
}

tokens = [
    'STMT_END',
    'EQUALS',
    'IDENTIFIER',
    'NUM_INT',
    'LPAREN',
    'RPAREN',
    'LBRACK',
    'RBRACK',
    'STRING',
    'COMMA',
    'NEWLINE',
    'LSQBRACK',
    'RSQBRACK',

    'PLUS',
    'MINUS',
    'MUL',

    'LSHIFT',
    'RSHIFT',

    'TRUE',
    'FALSE',

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
t_LSQBRACK = r'\['
t_RSQBRACK = r'\]'
t_EQ = '=='
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


def t_TRUE(t):
    'true'
    t.value = True

    return t


def t_FALSE(t):
    'false'
    t.value = False

    return t


def t_IDENTIFIER(t):
    r'[\$_a-zA-Z]\w*'
    t.type = reserved.get(t.value, t.type)

    return t


def t_NUM_INT(t):
    r'\d+'
    t.value = int(t.value)

    return t


def t_STRING(t):
    r'"(?:\\"|.)*?"'
    t.value = bytes(t.value.lstrip('"').rstrip('"'), "utf-8").decode("unicode_escape")

    return t


def t_error(t):
    raise UnexpectedChar("Caracter inesperado '%s' en linea %d" % (t.value[0], t.lineno))


def setup(source_file):
    lexical_analyzer.input(source_file)


lexer = lexical_analyzer.lex()
