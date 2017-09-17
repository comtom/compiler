from behave import given, when, then
from expects import *


@given('a mocked source {program}')
def mocked_source(context, program):
    context.error = None
    context.program = program


@then('compiler must remove comments and accept the input')
def check_valid_comments(context):
    pass


@then('compiler must not accept the input')
def check_invalid_comments(context):
    expect(context.error).to_not(be_none)
