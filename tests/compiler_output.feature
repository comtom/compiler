# Created by comtom at 8/25/17
Feature: Compiler output

  Scenario:
    Given existe un archivo de codigo program.code
    When el usuario invoca al compilador con el archivo como argumento
    Then el compilador devuelve el contenido del archivo

