import io
import os
import re
from codecs import open
from os import path
from setuptools import setup, find_packages


def read(*names, **kwargs):
    with io.open(os.path.join(os.path.dirname(__file__), *names),
                 encoding=kwargs.get("encoding", "utf8")) as file:
        return file.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def version():
    return find_version("compiler/__init__.py")


current_directory = path.abspath(path.dirname(__file__))


def local_file(name):
    return os.path.join(current_directory, name)

with open(local_file('README.md'), encoding='utf-8') as description_file:
    long_description = description_file.read()

print(long_description)


setup(
    name='compiler',
    version=version(),
    packages=find_packages(exclude=['tests']),
    url='https://github.com/Comtom/compiler',
    license='',
    author='Tomas Gonzalez Dowling',
    author_email='lucasrodeles@gmail.com, tomas@comtomtech.com',
    description='Code Language Compiler',
    long_description=long_description,
    keywords=['compiler'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'ply',
    ]
)
