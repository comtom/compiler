#!/usr/bin/env python
"""Wrapper module that calls syntax analyzer. This is neccesary in order to catch exceptions."""

import sys
import optparse
from src.syntax_analyzer import run_syntax_analyzer


DEBUG = True

def main(source_file):
    if DEBUG:
        run_syntax_analyzer()
    else:
        try:
            run_syntax_analyzer()
            return 0
        except Exception as error:
            sys.stderr.write('ERROR: %s' % str(error))
            return 1


if __name__ == '__main__':
    parser = optparse.OptionParser()

    source_file = ''
    parser.add_option('-s', '--source',
                      action="store", dest="source_file",
                      help="source code file")


    sys.exit(main(source_file))
