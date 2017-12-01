# Compiler
Compiladores UFASTA 2017


[![build_status](https://travis-ci.com/comtom/compiler.svg?token=v8Uz1yh4sMNd73DSo77q&branch=master)](https://travis-ci.com/comtom/compiler)


Instalacion


 * Descargar python https://www.python.org/downloads/ (para windows xp, se debera descargar la version 3.4.4: https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi)
 * Ejecutar instalador de python. Luego de seleccionar el directorio, en la pantalla "Customize python" seleccionar la opcion "Add python.exe to Path" (debe decir "will be installed on local hard drive")
 * Descomprimir el proyecto en el directorio C:\Documents and Settings\Administrador\Escritorio\compilador
 * Ejecutar una consola (Menu Inicio > Ejecutar, escribir cmd y presionar enter)
 * En la consola ejecutar cd C:\Documents and Settings\Administrador\Escritorio\compilador
 * Instalar dependencias: pip install -r requirements.txt
 * Instalar el compilador: python setup.py install
 * Ejecutar el compilador: python compiler/compile.py example.code
 * Para ejecutar los tests ejecutar en la consola: behave tests