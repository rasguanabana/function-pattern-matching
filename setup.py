from setuptools import setup

import re
import ast


version = 0.1

setup(
    name = 'function-pattern-matching',
    version = version,
    description = "",
    long_description = "",
    url = "https://github.com/rasguanabana/function-pattern-matching",
    author = "Adrian Włosiak",
    author_email = "adwlosiakh@gmail.com",
    license = "MIT",
    classifiers = [
        "Development Status :: 3 - Alpha", #? FIXME
        "Environment :: ", #any
        "Intended Audience :: ", #devs
        "License :: OSI Approved :: MIT License",
        "Operating System :: ", #any
        "Programming Language :: Python :: 3 :: Only", #depends?
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4", #what about these?
        "Programming Language :: Python :: 3.5",
    ],
    keywords = "",
    py_modules = ['function_pattern_matching'],
    entry_points = None #{'console_scripts': ['ytfs = ytfs.ytfs:main']} #FIXME
)
