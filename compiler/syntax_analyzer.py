"""Module that implements a syntax analyzer."""

from lexical_analyzer import lex
import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from calclex import tokens

output = ''


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
