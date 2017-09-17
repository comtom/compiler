from behave import given, when, then
from expects import *
from compiler.lexical_analyzer import setup
from compiler.syntax_analyzer import run_syntax_analyzer


@given('a program source file named {file}')
def filesource_exists(context, file):
    context.error = None
    context.file = file


@given('loads mocked source to verify output')
def load_mocked_source(context):
    context.tokens = "Token(PRINT,'print',2,1)Token(STRING,'hello world',2,7)Token(STMT_END,';',2,20)"
    context.program_code = 'print "hello world";'


@when('the user invokes the compiler with the program as an argument')
def invoke_compiler(context):
    if hasattr(context, 'file'):
        with open(context.file, 'r') as f:
            context.source_file_content = f.read().replace('\n', '')

        setup(context.source_file_content)
    else:
        setup(context.program)

    try:
        context.output = run_syntax_analyzer(False)
    except Exception as error:
        context.output = ''
        context.error = 'ERROR: %s' % str(error)


@then('input program is equal to output')
def check_output(context):

    expect(context.source_file_content).to(equal(context.program_code))
    expect(context.error).to(be_none)
    # TODO: hacer que contex.output sea stdout y no un objeto ylex
    # expect(context.tokens).to(equal(context.output))
