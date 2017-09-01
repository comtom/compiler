from behave import given, when, then
from expects import *

@given('existe un archivo de codigo')
def existe_codigo(context):
    pass


@when('el usuario invoca al compilador con el archivo: {archivo}')
def invocacion_compilador(context, archivo):
    context.salida = None


@then('el compilador devuelve el contenido del archivo')
def chequea_salida(context, archivo):
    expect(context.entrada).to(be(context.salida))
