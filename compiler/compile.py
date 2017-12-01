#!/usr/bin/env python
"""Wrapper que llama a syntax analyzer.
Es necesario para poder capturar las excepciones y mostrar los errores correspondientes."""

import sys
import os

from compiler import logger, errors
from compiler.lexical_analyzer import setup
from compiler.grammar import run_syntax_analyzer
from compiler.parser import symbols
from compiler.lexer.lexer import tokens

DEBUG = os.getenv('DEBUG', False) == 'True'


def main(source_file):
    lexer = setup(source_file)

    if DEBUG:
        run_syntax_analyzer(DEBUG, logger).parse(source_file, debug=True, lexer=lexer)
        print_out()
    else:
        try:
            run_syntax_analyzer(DEBUG, logger).parse(source_file, lexer=lexer)
            print_out()
            return 0
        except Exception as error:
            sys.stderr.write('ERROR: %s' % str(error))

    return 1


def print_out():
    logger.info('------------------------------')
    logger.info('Tokens')
    for token in tokens:
        logger.info(token)
    logger.info('------------------------------')
    logger.info('Table de simbolos')
    logger.info(symbols.table()['symbols'].keys())

    if errors:
        logger.info('------------------------------')
        for error in errors:
            logger.error(error)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Error: Debe indicar el archivo a compilar: %s archivo_codigo_fuente.code" % __file__)
    else:
        with open(sys.argv[1]) as f:
            source_file = f.read()

    sys.exit(main(source_file))
