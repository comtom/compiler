from behave import given, when, then
from expects import *
from compiler.lexical_analyzer import setup
from compiler.grammar import run_syntax_analyzer


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
        lexer = setup(context.source_file_content)
    else:
        lexer = setup('programa{ %s }' % context.program)

    try:
        context.output = run_syntax_analyzer(False).parse(context.program, lexer=lexer)
    except Exception as error:
        context.output = ''
        context.error = 'ERROR: %s' % str(error)


@then('input program is equal to output')
def check_output(context):
    expect(context.source_file_content).to(equal(context.program_code))
    expect(context.error).to(be_none)
    # TODO: hacer que contex.output sea stdout y no un objeto
    # expect(context.tokens).to(equal(context.output))


@then('compiler must accept the input')
def accept_input_program(context):
    pass


@given('a mocked source {program}')
def mocked_source(context, program):
    context.error = None
    context.program = program


@then('compiler must remove comments and accept the input')
def check_valid_comments(context):
    expect(context.error).to(be_none)


@then('compiler must not accept the input')
def check_invalid_comments(context):
    expect(context.error).to_not(be_none)


@then('compiler must reject the input')
def reject_input_program(context):
    expect(context.error).to_not(be_none)
