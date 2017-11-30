#!/usr/bin/env python
"""Wrapper que llama a syntax analyzer.
Es necesario para poder capturar las excepciones y mostrar los errores correspondientes."""

import sys
import os
import logging

from compiler.lexical_analyzer import setup
from compiler.grammar import run_syntax_analyzer


DEBUG = os.getenv('DEBUG', False) == 'True'


def main(source_file):
    log = logging.getLogger()
    lexer = setup(source_file)

    if DEBUG:
        run_syntax_analyzer(DEBUG, log).parse(input=source_file, debug=True, lexer=lexer)
    else:
        try:
            res = run_syntax_analyzer(DEBUG, log).parse(source_file, lexer=lexer)
            # for node in res.children:
            #     node.eval()
            return 0
        except Exception as error:
            sys.stderr.write('ERROR: %s' % str(error))
            return 1


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Error: Debe indicar el archivo a compilar: %s archivo_codigo_fuente.code" % __file__)
    else:
        with open(sys.argv[1]) as f:
            source_file = f.read()

    sys.exit(main(source_file))
