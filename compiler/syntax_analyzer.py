"""Module that implements a syntax analyzer."""

import ply.yacc as yacc
from lexical_analyzer import *
from abstract_syntax_tree import PrintStatement, Identifier, If, While, InstructionList, BaseExpression, Primitive, Assignment


disable_warnings = False

precedence = (
    ('left', 'PLUS'),
    ('left', 'MUL'),
)


def p_statement(p):
    '''
    statement : identifier
              | expression
              | if_statement
    '''
    p[0] = p[1]


def p_identifier(p):
    '''
    identifier : IDENTIFIER
    '''
    p[0] = Identifier(p[1])


def p_expression(p):
    '''
    expression : primitive
               | STRING
               | identifier
    '''
    p[0] = p[1]


def p_ifstatement(p):
    '''
    if_statement : IF expression LBRACK statement_list RBRACK
    '''
    p[0] = If(p[2], p[4])


def p_ifstatement_else(p):
    '''
    if_statement : IF expression LBRACK statement_list RBRACK ELSE LBRACK statement_list RBRACK
    '''
    p[0] = If(p[2], p[4], p[8])


def p_ifstatement_else_if(p):
    '''
    if_statement : IF expression LBRACK statement_list RBRACK ELSE if_statement
    '''
    p[0] = If(p[2], p[4], p[7])


def p_statement_list(p):
    '''
    statement_list : statement
                   | statement_list statement
    '''
    if len(p) == 2:
        p[0] = InstructionList([p[1]])
    else:
        p[1].children.append(p[2])
        p[0] = p[1]


def p_primitive(p):
    '''
    primitive : NUM_INT
              | STRING
    '''
    if isinstance(p[1], BaseExpression):
        p[0] = p[1]
    else:
        p[0] = Primitive(p[1])


def p_assignable(p):
    '''
    assignable : primitive
               | expression
    '''
    p[0] = p[1]


def p_assign(p):
    '''
    expression : identifier EQUALS assignable STMT_END
    '''
    p[0] = Assignment(p[1], p[3])



def p_paren(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    p[0] = p[2] if isinstance(p[2], BaseExpression) else Primitive(p[2])


def p_while_loop(p):
    '''
    statement : WHILE expression LBRACK statement_list RBRACK
    '''
    p[0] = While(p[2], p[4])


def p_print_statement(p):
    '''
    statement : PRINT STRING STMT_END
    '''
    p[0] = PrintStatement(p[2])


def p_error(p):
    if p is not None:
        raise ParserSyntaxError("Error de sintaxis en la linea %d, token no reconocido: '%s'" % (p.lineno, p.value))

    raise ParserSyntaxError("Error en la terminacion del archivo.")


def run_syntax_analyzer(DEBUG):
    while True:
        token = lexer.token()

        if token is None:
            break
        else:
            if DEBUG:
                print(str(token))

    return yacc.yacc(errorlog=yacc.NullLogger()) if disable_warnings else yacc.yacc()
