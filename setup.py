from __future__ import with_statement
from setuptools import setup

version = '0.99a2'

with open("README.rst", mode='r') as fp:
    long_desc = fp.read()

setup(
    name = 'function-pattern-matching',
    version = version,
    description = "Pattern matching and guards for Python functions",
    long_description = long_desc,
    url = "https://github.com/rasguanabana/function-pattern-matching",
    author = "Adrian Włosiak",
    author_email = "adwlosiakh@gmail.com",
    license = "MIT",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords = "pattern matching guards",
    py_modules = ['function_pattern_matching'],
    install_requires = ['six']
)
