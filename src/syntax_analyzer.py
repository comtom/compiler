"""Module that implements a syntax analyzer."""

from src.lexical_analyzer import lex


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
