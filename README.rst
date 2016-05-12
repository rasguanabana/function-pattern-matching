function-pattern-matching
*************************

**function-pattern-matching** (**fpm** for short) is a module which introduces Erlang-style
`multiple clause defined functions <http://erlang.org/doc/reference_manual/functions.html>`_ and
`guard sequences <http://erlang.org/doc/reference_manual/functions.html#id77457>`_ to Python.

This module is both Python 2 and 3 compatible.

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

  - ``rguard``: Wrapper for ``guard`` which converts first positional decorator argument to relguard. See Relguards_.

  - ``raguard``: Like ``rguard``, but converts return annotation. See Relguards_.

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

**Note:** This module does not aim to be used on production scale or in a large sensitive application (but I'd be
happy if someone decided to use it in his/her project). I think of it more as a fun project which shows how
flexible Python can be (and as a good training for myself).

I'm aware that it's somewhat against duck typing and EAFP (easier to ask for forgiveness than for permission)
philosophy employed by the language, but obviously there *are* some cases when preliminary checks are useful and
make code (and life) much simpler.

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

**Note:** It is not possible to put guards on varying arguments (\*args, \**kwargs).

List of provided guard functions
................................

Every following function returns/is a callable which takes only one parameter - the call argument that is to be
checked.

- ``_`` - Catch-all. Returns ``True`` for any input. Actually, this can take any number of arguments.
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
- ``eFalse`` - checks if input evaluates to ``False`` (converts input to ``bool``)
- ``In(val)`` - checks if input is in *val* (uses ``in`` operator)
- ``notIn(val)`` - checks if input is not in *val* (uses ``not in`` operator)

Custom guards
.............

Although it is not advised (at least for simple checks), you can create your own guards:

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

**Note:** It is not recommended to create your own guard functions. In most cases combinations of the ones shipped with
fpm should be all you need.

Define guards for function arguments
....................................

There are two ways of defining guards:

- As decorator arguments

  - positionally: guards order will match decoratee's (the function that is to be decorated) arguments order.

    .. code-block:: python

        @fpm.guard(fpm.isoftype(int) & fpm.ge(0), fpm.isiterable)
        def func(number, iterable):
            pass

  - as keyword arguments: e.g. guard under name *a* will guard decoratee's argument named *a*.

    .. code-block:: python

        @fpm.guard(
            number = fpm.isoftype(int) & fpm.ge(0),
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

If you try to declare guards using both methods at once, then annotations get ignored and are left untouched.

Relguards
---------

Relguard is a kind of guard that checks relations between arguments (and/or external variables). ``fpm`` implements
them as functions (wrapped in ``RelGuard`` object) whose arguments are a subset of decoratee's arguments (no arguments
is fine too).

Define relguard
...............

There are a few ways of defining a relguard.

- Using ``guard`` with the first (and only) positional non-keyword argument of type ``RelGuard``:

  .. code-block:: python

      @fpm.guard(
          fpm.relguard(lambda a, c: a == c), # converts lambda to RelGuard object in-place
          a = fpm.isoftype(int) & fpm.eTrue,
          b = fpm.Isnot(None)
      )
      def func(a, b, c):
          pass

- Using ``guard`` with the return annotation holding a ``RelGuard`` object (Python 3 only):

  .. code-block:: python

      @fpm.guard
      def func(a, b, c) -> fpm.relguard(lambda a, b, c: a != b and b < c):
          pass

- Using ``rguard`` with a regular callable as the first (and only) positional non-keyword argument.

  .. code-block:: python

      @fpm.rguard(
          lambda a, c: a == c, # rguard will try converting this to RelGuard object
          a = fpm.isoftype(int) & fpm.eTrue,
          b = fpm.Isnot(None)
      )
      def func(a, b, c):
          pass

- Using ``raguard`` with a regular callable as the return annotation.

  .. code-block:: python

      @fpm.raguard
      def func(a, b, c) -> lambda a, b, c: a != b and b < c: # raguard will try converting lambda to RelGuard object
          pass

As you can see, when using ``guard`` you have to manually convert functions to ``RelGuard`` objects with ``relguard``
method. By using ``rguard`` or ``raguard`` decorators you don't need to do it by yourself, and you get a bit cleaner
definition.

Multiple function clauses
-------------------------

With ``case`` decorator you are able to define multiple clauses of the same function.

When such a function is called with some arguments, then the first matching clause will be executed. Matching clause
will be the one that didn't raise a ``GuardError`` when called with given arguments.

**Note:** using ``case`` or ``dispatch`` (discussed later) disables default functionality of default argument values.
Functions with varying arguments (\*args, \**kwargs) and keyword-only arguments (py3-only) are not supported.

Example:

.. code-block:: python

    @fpm.case
    def func(a=0): print("zero!")

    @fpm.case
    def func(a=1): print("one!")

    @fpm.case
    @fpm.guard(fpm.gt(9000))
    def func(a): print("IT'S OVER 9000!!!")

    @fpm.case
    def func(a): print("some var:", a) # catch-all clause

    >>> func(0)
    'zero!'
    >>> func(1)
    'one!'
    >>> func(9000.1)
    "IT'S OVER 9000!!!"
    >>> func(1337)
    'some var: 1337'

If no clause matches, then ``MatchError`` is raised. The example shown above has a catch-all clause, so ``MatchError``
will never occur.

Different arities (argument count) are allowed and are dispatched separetely.

Example:

.. code-block:: python

    @fpm.case
    def func(a=1, b=1, c):
        return 1

    @fpm.case
    def func(a, b, c):
        return 2

    @fpm.case
    def func(a=1, b=1, c, d):
        return 3

    @fpm.case
    def func(a, b, c, d):
        return 4

    >>> func(1, 1, 'any')
    1
    >>> func(1, 0, 0.5)
    2
    >>> func(1, 1, '', '')
    3
    >>> func(1, 0, 0, '')
    4

As you can see, clause order matters only for same-arity clauses. 4-arg catch-all does not affect any 3-arg definition.

Define multi-claused functions
..............................

There are three ways of defining a pattern for a function clause:

- Specify exact values as decorator arguments (positional and/or keyword)

  .. code-block:: python

      @fpm.case(1, 2, 3)
      def func(a, b, c):
          pass
      
      @fpm.case(1, fpm._, 0)
      def func(a, b, c):
          pass

      @fpm.case(b=10)
      def func(a, b, c):
          pass

- Specify exact values as default arguments

  .. code-block:: python

      @fpm.case
      def func(a=0):
          pass

      @fpm.case
      def func(a=10):
          pass

      @fpm.case
      def func(a=fpm._, b=3):
          pass

- Specify guards for clause to match

  .. code-block:: python

      @fpm.case
      @fpm.guard(fpm.eq(0) & ~fpm.isoftype(float))
      def func(a):
          pass

      @fpm.case
      @fpm.guard(fpm.gt(0))
      def func(a):
          pass

      @fpm.case
      @fpm.guard(fpm.Is(None))
      def func(a):
          pass

``dispatch`` decorator
......................

``dispatch`` decorator is similar to ``case``, but it lets you to define argument types to match against. You can
specify types either as decorator arguments or default values (or as guards, of course, but it makes using ``dispatch``
pointless).

Example:

.. code-block:: python

    @fpm.dispatch(int, int)
    def func(a, b):
        print("integers")

    @fpm.dispatch
    def func(a=float, b=float):
        print("floats")

    >>> func(1, 1)
    'integers'
    >>> func(1.0, 1.0)
    'floats'

Examples (the useful ones)
==========================

Still working on this section!

- Ensure that an argument is a list of strings. Prevent feeding string accidentally, which can cause some headache,
  since both are iterables.

  - Option 1: do not allow strings

    .. code-block:: python

        # thanks to creshal from HN for suggestion

        lookup = {
            "foo": 1,
            "bar": 2,
            "baz": 3
        }

        @fpm.guard
        def getSetFromDict(
            dict_, # let it throw TypeError if not a dict. Will be more descriptive than a GuardError.
            keys: ~fpm.isoftype(str)
        ):
            "Returns a subset of elements of dict_"
            ret_set = set()
            for key in keys:
                try:
                    ret_set.add(dict_[key])
                except KeyError:
                    pass
            return ret_set

        getSetFromDict(lookup, ['foo', 'baz', 'not-in-lookup']) # will return two-element set
        getSetFromDict(lookup, 'foo') # raises GuardError, but would return empty set without guard!

Similar solutions
=================

- `singledispatch <https://docs.python.org/3/library/functools.html#functools.singledispatch>`_ from functools
- `pyfpm <https://github.com/martinblech/pyfpm>`_
- `patmatch <http://svn.colorstudy.com/home/ianb/recipes/patmatch.py>`_
- http://blog.chadselph.com/adding-functional-style-pattern-matching-to-python.html
- http://www.artima.com/weblogs/viewpost.jsp?thread=101605 (by Guido van Rossum, BDFL)

License
=======

MIT (c) Adrian Włosiak
