"""Module that implements a syntax analyzer."""

from src.lexical_analyzer import get_token


output = ''


def run_syntax_analyzer():
    global output

    while True:
        token = get_token().lexeme

        if token == '$':
            print(output)
            break
        else:
            output += token
