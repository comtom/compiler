from behave import given, when, then
from expects import *
from compiler.lexical_analyzer import setup
from compiler.syntax_analyzer import run_syntax_analyzer


@given('a program source file named {file}')
def filesource_exists(context, file):
    context.file = file


@when('the user invokes the compiler with the program as an argument')
def invoke_compiler(context):
    if hasattr(context, 'file'):
        setup(context.file)
    else:
        setup(context.program)
    context.output = run_syntax_analyzer(True)
    context.tokens = "Token(PRINT,'print',2,1)Token(STRING,'hello world',2,7)Token(STMT_END,';',2,20)"
    context.program_code = 'print "hello world";'


@then('input program is equal to output')
def check_output(context):
    with open(context.file, 'r') as f:
        data = f.read().replace('\n', '')

    expect(data).to(equal(context.program_code))
    expect(context.tokens).to(equal(context.output))
