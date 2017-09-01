# Created by comtom at 8/25/17
Feature:

  Scenario:
    Given existe un archivo de codigo
    When el usuario invoca al compilador con el archivo como argumento
    Then el compilador devuelve el contenido del archivo.doc

