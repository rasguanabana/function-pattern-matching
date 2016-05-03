from collections import defaultdict
from functools import wraps
import six
import inspect

# GENERAL #

class GuardError(Exception): # needed? MatchError isn't sufficient?
    "Guard haven't let argument pass."
    pass

class MatchError(Exception):
    "No match for function call."
    pass

class WontMatchError(Exception):
    "Case declared after catch-all or identical case."
    pass

class MixedPatternDefinitionError(Exception):
    "Raised when pattern is defined both as `case` arguments and function defaults."
    pass

class _():
    """The "don't care" value."""
    def __repr__(self):
        return "_"

_ = _() # we need just one and only one instance.

# CASE #
#
#class Multi_function():
#    def __init__(self):
#        self.functions = list()
#
#    @staticmethod
#    def __ismatching(arg_tuple, function_head):
#        pass
#
#    def __call__(self, *args):
#        # returns first matching head:
#        function_body = next(
#                (f.body for f in self.functions if __ismatching(args, f.head)), # generator finds only matching heads
#                lambda: raise MatchError # default value, when next() hit StopIteration (generator was empty)
#                )                        # so when no match was found, MatchError is raised.
#        return function_body(*args) # execute and return result.
#
#    def append(self, *):
#        pass
#
#
#function_refs = defaultdict(lambda: defaultdict(Multi_function)) # needed for case to track multi-headed functions.
#    # module name -> fun qualname -> Multi_function object
#
#def case(*args):
#    "Main wrapper. *args can be pattern to match against, or directly a function head."
#
#    def decorator(decoratee, pattern=None):
#        "Actual decorator. Registers function head (pattern) and corresponding function body."
#
#        # TODO: many try's to keep compat with py2.
#        # needed:
#        # - extract pattern from (case *args)/(fun arg defaults)/annotations
#        # then:
#        # - function_refs[module][fun_name].append(pattern, body), if no errors/exceptions.
#
#        params = inspect.signature(decoratee)
#        # TODO: continue
#
# GUARD #

class GuardFunc():
    def __init__(self, test):
        if not callable(test):
            raise ValueError("Guard test has to be callable")

        try:
            sig_params = inspect.signature(test).parameters
        except AttributeError:
            # python 2
            arg_spec = inspect.getargspec(test)
            if len(arg_spec.args) != 1:
                raise ValueError("Guard test has to have only one positional (not varying) argument")
        else:
            # continue in case signature is available (six below may be redundant, as it most probably is python 3)
            param = six.next(six.itervalues(sig_params)) # get first (and only) parameter.
            if not (len(sig_params) == 1 and             #       <---------' checked here
                    param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)): # accept only not varying positional
                raise ValueError("Guard test has to have only one positional (not varying) argument")

        self.test = test

    def _otherisguard(method):
        @wraps(method)
        def checks(self, other):
            if not isinstance(other, GuardFunc):
                raise TypeError("The right-hand operand has to be instance of GuardFunc")
            return method(self, other)

        return checks

    def __invert__(self):
        return GuardFunc(lambda inp: not self.test(inp))

    @_otherisguard
    def __and__(self, other):
        return GuardFunc(lambda inp: (self.test(inp) & other.test(inp)))

    @_otherisguard
    def __or__(self, other):
        return GuardFunc(lambda inp: (self.test(inp) | other.test(inp)))

    @_otherisguard
    def __xor__(self, other):
        return GuardFunc(lambda inp: (self.test(inp) ^ other.test(inp)))

    def __call__(self, inp):
        try:
            ret = bool(self.test(inp))
        except TypeError:
            ret = False
        return ret

def makeguard(decoratee):
    "Decorator"
    return GuardFunc(decoratee)

def eq(val):
    return GuardFunc(lambda inp: inp == val)
def ne(val):
    return GuardFunc(lambda inp: inp != val)
def lt(val):
    return GuardFunc(lambda inp: inp < val)
def le(val):
    return GuardFunc(lambda inp: inp <= val)
def gt(val):
    return GuardFunc(lambda inp: inp > val)
def ge(val):
    return GuardFunc(lambda inp: inp >= val)

def Is(val):
    return GuardFunc(lambda inp: inp is val)
def Isnot(val):
    return GuardFunc(lambda inp: inp is not val)

def isoftype(type_):
    return GuardFunc(lambda inp: isinstance(inp, type_))

@makeguard
def isiterable(inp):
    try:
        iter(inp)
    except TypeError:
        return False
    else:
        return True

@makeguard
def eTrue(inp):
    return bool(inp)

@makeguard
def eFalse(inp):
    return not bool(inp)

def In(val):
    _ in val # simple test for in support
    return GuardFunc(lambda inp: inp in val)
def notIn(val):
    _ in val # simple test for in support
    return GuardFunc(lambda inp: inp not in val)


#def guard(*args, **kwargs):
#    "Checks if arguments meet criteria when the function is called."
#
#    def decorator(decoratee, pattern=None):
#        "Actual decorator."
#
#        @wraps(decoratee)
#        def guarded(*args, **kwargs):
#            
#            # TODO:
