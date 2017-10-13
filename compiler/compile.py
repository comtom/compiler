#!/usr/bin/env python
"""Wrapper que llama a syntax analyzer.
Es necesario para poder capturar las excepciones y mostrar los errores correspondientes."""

import sys
import os

from compiler.lexical_analyzer import setup
from compiler.syntax_analyzer import run_syntax_analyzer


DEBUG = os.getenv('DEBUG', False) == 'True'


def main(source_file):
    setup(source_file)

    if DEBUG:
        run_syntax_analyzer(DEBUG)
    else:
        try:
            run_syntax_analyzer(DEBUG)
            return 0
        except Exception as error:
            sys.stderr.write('ERROR: %s' % str(error))
            return 1


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Error: Debe indicar el archivo a compilar: %s archivo_codigo_fuente.code" % __file__)
    else:
        with open(sys.argv[1]) as f:
            source_file = data = f.read()

    sys.exit(main(source_file))
