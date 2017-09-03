from behave import given, when, then
from expects import *


@given('a program source file named {file}')
def filesource_exists(context, file):
    context.file = file


@when('the user invokes the compiler with the program as an argument')
def invoke_compiler(context):
    context.output = None   # invoke compiler


@then('input program is equal to output')
def check_output(context):
    with open(context.file, 'r') as f:
        data = f.read().replace('\n', '')

    expect(data).to(be(context.output))
