function-pattern-matching
*************************

**function-pattern-matching** is a module which introduces Erlang-style `multiple clause defined functions
<http://erlang.org/doc/reference_manual/functions.html>`_ and
`guard sequences <http://erlang.org/doc/reference_manual/functions.html#id77457>`_.

This module is both Python 2 and 3 compatible.

.. warning:: Readme and docs under construction.

.. contents:: Table of contents

Introduction
============

Two families of decorators are introduced:

- ``case``: allows multiple function clause definitions and dispatches to correct one. Dispatch happens on the values
  of call arguments or, more generally, when call arguments' values match specified guard definitions.
  - ``dispatch``: convenience decorator for dispatching on argument types. Equivalent to using ``case`` and ``guard``
    with type checking.
- ``guard``: allows arguments' values filtering and raises ``GuardError`` when argument value does not pass through
  argument guard.
  - ``rguard``: Wrapper for ``guard`` which converts first positional decorator argument to relguard. See `example`_.
  - ``raguard``: Like ``rguard``, but converts return annotation. See `example`_.

Usage example:

- All Python versions:

.. code-block:: python

    import function_pattern_matching as fpm

    @fpm.case
    def factorial(n=0):
        return 1

    @fpm.case
    @fpm.guard(fpm.is_int & fpm.gt(0))
    def factorial(n):
        return n * factorial(n - 1)

- Python 3 only:

.. code-block:: python

    import function_pattern_matching as fpm

    @fpm.case
    def factorial(n=0):
        return 1

    @fpm.case
    @fpm.guard
    def factorial(n: fpm.is_int & fpm.gt(0)): # Guards specified as annotations
        return n * factorial(n - 1)

Of course that's a poor implementation of factorial, but illustrates the idea in a simple way.

.. note::

    This module does not aim to be used on production scale or in a large sensitive application. I think of it more
    as a fun project which shows how flexible Python can be (and as a good training :)

    I'm aware that it's somewhat against duck typing and EAFP philosophy employed by the language, but obviously there
    *are* some cases when preliminary checks are useful and make code (and life) much simpler.

Installation
============

function-pattern-matching can be installed with pip::

    $ pip install function-pattern-matching

Module will be available as ``function_pattern_matching``. It is recommended to import as ``fpm``.

Usage
=====

Guards
------

With ``guard`` decorator it is possible to filter function arguments upon call. When argument value does not pass
through specified guard, then ``GuardError`` is raised.

When global setting ``strict_guard_definitions`` is set ``True`` (the default value), then only ``GuardFunc``
instances can be used in guard definitions. If it's set to ``False``, then any callable is allowed, but it is **not**
recommended, as guard behaviour may be unexpected (``RuntimeWarning`` is emitted), e.g. combining regular callables
will not work.

``GuardFunc`` objects can be negated with ``~`` and combined together with ``&``, ``|`` and ``^`` logical operators.
Note however, that *xor* isn't very useful here.

List of provided guard functions
................................

Every following function returns/is a callable which takes only one parameter - the call argument that is to be
checked.

- ``eq(val)`` - checks if input is equal to *val*
- ``ne(val)`` - checks if input is not equal to *val*
- ``lt(val)`` - checks if input is less than *val*
- ``le(val)`` - checks if input is less or equal to *val*
- ``gt(val)`` - checks if input is greater than *val*
- ``ge(val)`` - checks if input is greater or equal to *val*
- ``Is(val)`` - checks if input is *val* (uses ``is`` operator)
- ``Isnot(val)`` - checks if input is not *val* (uses ``is not`` operator)
- ``isoftype(_type)`` - checks if input is instance of *_type* (uses ``isintance`` function)
- ``isiterable`` - checks if input is iterable
- ``eTrue`` - checks if input evaluates to ``True`` (converts input to ``bool``)
- ``eFalse`` - checks if input is evaluates to ``False`` (converts input to ``bool``)
- ``In(val)`` - checks if input is in *val* (uses ``in`` operator)
- ``notIn(val)`` - checks if input is not in *val* (uses ``not in`` operator)

Custom guards
.............

Although it is not advised, you can create your own guards:
- by using ``makeguard`` decorator on your test function.
- by writing a function that returns a ``GuardFunc`` object initialised with a test function.

Note that a test function must have only one positional argument.

Examples:

.. code-block:: python

    # use decorator
    @fpm.makeguard
    def is_not_zero_nor_None(inp):
        return inp != 0 and inp is not None

    # return GuardFunc object
    def is_not_val_nor_specified_thing(val, thing):
        return GuardFunc(lambda inp: inp != val and inp is not thing)

    # equivalent to (fpm.ne(0) & fpm.Isnot(None)) | (fpm.ne(1) & fpm.Isnot(some_object))
    @fpm.guard(is_not_zero_nor_None | is_not_val_nor_specified_thing(1, some_object))
    def guarded(argument):
        pass

The above two are very similar, but the second one allows creating function which takes multiple arguments to construct
actual guard.

.. note:: It is not recommended to create your own guard functions. Use combinations of the ones shipped with fpm.

Define guards for function arguments
....................................

There are two ways of defining guards:

- As decorator arguments
  - positionally: guards order will match decoratee's (the function being decorated) arguments order.

    .. code-block:: python

        @fpm.guard(fpm.isoftype(int) & fpm.ge(0), fpm.isiterable)
        def func(number, iterable):
            pass

  - as keyword arguments: e.g. guard under name *a* will guard decoratee's argument named *a*.

    .. code-block:: python

        @fpm.guard(
            name = fpm.isoftype(int) & fpm.ge(0),
            iterable = fpm.isiterable
        )
        def func(number, iterable):
            pass

- As annotations (Python 3 only)

  .. code-block:: python

      @fpm.guard
      def func(
          number: fpm.isoftype(int) & fpm.ge(0),
          iterable: fpm.isiterable
      ): # this is NOT an emoticon
          pass

Relguard
--------

Define relguard
...............

Multiple function clauses
-------------------------

Examples (the useful ones)
==========================

Similar solutions
=================

- singledispatch from functools
- pyfpm
- http://blog.chadselph.com/adding-functional-style-pattern-matching-to-python.html
- http://svn.colorstudy.com/home/ianb/recipes/patmatch.py
- http://www.artima.com/weblogs/viewpost.jsp?thread=101605 (Guido)

License
=======

MIT (c) Adrian Włosiak
