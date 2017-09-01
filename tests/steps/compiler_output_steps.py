from behave import given, when, then
from expects import *


@given('existe un archivo de codigo {file}')
def filesource_exists(context, file):
    context.file = file


@when('el usuario invoca al compilador con el archivo como argumento')
def invoke_compiler(context):
    context.output = None   # invoke compiler


@then('el compilador devuelve el contenido del archivo')
def check_output(context):
    with open(context.file, 'r') as f:
        data = f.read().replace('\n', '')

    expect(data).to(be(context.output))
