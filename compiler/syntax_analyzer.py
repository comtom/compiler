"""Module that implements a syntax analyzer."""


import ply.yacc as yacc
from lexical_analyzer import tokens
from lexical_analyzer import lex


disable_warnings = False

precedence = (
    ('left', 'NOT'),
    ('left', 'PLUS'),
    ('left', 'MUL'),
    ('right', 'UMINUS'),
    ('right', 'UPLUS'),
)

output = ''
symbol_table = {}



def run_syntax_analyzer():
    global output

    while True:
        token = lex.token()

        if token is None:
            print(output)
            break

        # TODO: Borrar esto, solamente para probar que la entrada es igual a la salida
        else:
            output += token

    return yacc.yacc(errorlog=yacc.NullLogger()) if disable_warnings else yacc.yacc()
