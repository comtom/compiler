"""Module that implements a lexical analyzer."""


class Token:
    def __init__(self, lexeme):
        self._lexeme = lexeme

    @property
    def type(self):
        """returns token type"""
        pass

    @property
    def lexeme(self):
        """returns a lexeme"""
        pass


class InputBuffer:
    def __init__(self, input_string):
        self._string = input_string
        self._position = -1

    def __next__(self):
        self._position += 1
        return Token(self._string[self._position])



def get_token():
    """returns a token object."""

    return Token('a')
