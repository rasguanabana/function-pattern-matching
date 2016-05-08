import inspect
import six
import types
import warnings
from collections import defaultdict, OrderedDict
try:
    from inspect import _ParameterKind as p_kind
except ImportError:
    class p_kind():
        POSITIONAL_ONLY = 1
        POSITIONAL_OR_KEYWORD = 2
        VAR_POSITIONAL = 3
        KEYWORD_ONLY = 4
        VAR_KEYWORD = 5
try:
    from types import SimpleNamespace
except ImportError:
    pass

# GENERAL #

strict_guard_definitions = True # only instances of GuardFunc and RelGuard can be used as guards.
                                # if set to False, then any callable is allowed, but may cause unexpected behaviour.

class GuardError(Exception): # FIXME: needed? MatchError isn't sufficient?
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
    def __call__(*args, **kwargs):
        return True
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
# GUARDS #

def _getfullargspec_p(func):
    """Gets uniform full arguments specification of func, portably."""

    try:
        sig = inspect.signature(func)
        sig_params = sig.parameters
    except AttributeError: # signature method not available
        # try getfullargspec is present (pre 3.3)
        try:
            arg_spec = inspect.getfullargspec(func)
        except AttributeError: # getfullargspec method not available
            arg_spec = inspect.getargspec(func) # py2, trying annotations will fail.

    else: # continue conversion for py >=3.3
        arg_spec = SimpleNamespace() # available since 3.3, just like signature, so it's ok to use it here.

        def _arg_spec_helper(kinds=(), defaults=False, kwonlydefaults=False, annotations=False):
            for arg_name, param in sig_params.items():
                if not defaults and not kwonlydefaults and not annotations and param.kind in kinds:
                    yield arg_name
                elif sum((defaults, kwonlydefaults, annotations)) > 1:
                    raise ValueError("Only one of 'defaults', 'kwonlydefaults' or 'annotations' can be True simultaneously")
                elif param.default is not inspect._empty:
                    if defaults and param.kind in (p_kind.POSITIONAL_OR_KEYWORD, p_kind.POSITIONAL_ONLY):
                        yield param.default
                    elif kwonlydefaults and param.kind is p_kind.KEYWORD_ONLY:
                        yield (arg_name, param.default)
                elif annotations and param.annotation is not inspect._empty:
                    yield (arg_name, param.annotation)

        arg_spec.args = tuple(_arg_spec_helper((p_kind.POSITIONAL_OR_KEYWORD, p_kind.POSITIONAL_ONLY)))
        arg_spec.varargs = six.next(_arg_spec_helper((p_kind.VAR_POSITIONAL,)), None)
        arg_spec.kwonlyargs = tuple(_arg_spec_helper((p_kind.KEYWORD_ONLY,)))
        arg_spec.varkw = six.next(_arg_spec_helper((p_kind.VAR_KEYWORD,)), None)
        arg_spec.keywords = arg_spec.varkw # getargspec compat
        arg_spec.defaults = tuple(_arg_spec_helper(defaults=True)) or None
        arg_spec.kwonlydefaults = dict(_arg_spec_helper(kwonlydefaults=True))
        arg_spec.annotations = dict(_arg_spec_helper(annotations=True))
        if sig.return_annotation is not inspect._empty:
            arg_spec.annotations['return'] = sig.return_annotation

    return arg_spec

def _getparams(func):
    """Get tuple of arg name and kind pairs."""

    arg_spec = _getfullargspec_p(func)

    # create tuples for each kind
    args = tuple((arg, p_kind.POSITIONAL_OR_KEYWORD) for arg in arg_spec.args)
    varargs = ((arg_spec.varargs, p_kind.VAR_POSITIONAL),) if arg_spec.varargs else ()
    try:
        kwonlyargs = tuple((arg, p_kind.KEYWORD_ONLY) for arg in arg_spec.kwonlyargs)
    except AttributeError: # python2
        kwonlyargs = ()
    varkw = ((arg_spec.varkw, p_kind.VAR_KEYWORD),) if arg_spec.keywords else ()

    return args + varargs + kwonlyargs + varkw

class GuardFunc():
    def __init__(self, test):
        if not callable(test):
            raise ValueError("Guard test has to be callable")

        # check if test signature is ok
        test_args = _getparams(test)

        if len(tuple(arg for arg in test_args
                     if arg[1] in (p_kind.POSITIONAL_ONLY, p_kind.POSITIONAL_OR_KEYWORD))) != 1:
            raise ValueError("Guard test has to have only one positional (not varying) argument")

        def apply_try_conv_to_bool(function, arg):
            try:
                return bool(function(arg)) # test must always return boolean, so convert asap.
            except TypeError: # occures when unorderable types are compared, but we don't want TypeError to be raised.
                return False  # couldn't compare? then guard must say no.

        self.test = lambda inp: apply_try_conv_to_bool(test, inp)

    def _isotherguard(method):
        @six.wraps(method)
        def checks(self, other):
            if not isinstance(other, GuardFunc):
                raise TypeError("The right-hand operand has to be instance of GuardFunc")
            return method(self, other)

        return checks

    def __invert__(self):
        return GuardFunc(lambda inp: not self.test(inp))

    @_isotherguard
    def __and__(self, other):
        return GuardFunc(lambda inp: (self.test(inp) & other.test(inp)))

    @_isotherguard
    def __or__(self, other):
        return GuardFunc(lambda inp: (self.test(inp) | other.test(inp)))

    @_isotherguard
    def __xor__(self, other):
        return GuardFunc(lambda inp: (self.test(inp) ^ other.test(inp)))

    def __call__(self, inp):
        return self.test(inp)

    def __bool__(self):
        return self.__call__()
    def __nonzero__(self):
        return self.__call__()

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


class RelGuard():
    def __init__(self, test):
        if not callable(test):
            raise ValueError("Relguard test has to be callable")

        # extract simplified signature
        test_args = _getparams(test)

        # varying args are not allowed, they make no sense in reguards.
        _kinds = {x[1] for x in test_args}
        if (p_kind.POSITIONAL_ONLY in _kinds or
                p_kind.VAR_POSITIONAL in _kinds or
                p_kind.VAR_KEYWORD in _kinds):
            raise ValueError("Relguard test must take only named not varying arguments")

        self.test = test
        self.__argnames__ = {x[0] for x in test_args}

    def __call__(self, **kwargs):
        try:
            return bool(self.test(**{arg_name: arg_val for arg_name, arg_val in kwargs.items() if arg_name in self.__argnames__}))
        except TypeError: # occures when unorderable types are compared, but we don't want TypeError to be raised.
            return False

def relguard(decoratee):
    "Decorator"
    return RelGuard(decoratee)


def guard(*dargs, **dkwargs):
    "Checks if arguments meet criteria when the function is called."

    def decorator(decoratee):
        "Actual decorator."

        # get arg_spec
        arg_spec = _getfullargspec_p(decoratee)

        # parse dargs'n'dkwargs
        try:
            arg_list = arg_spec.args + arg_spec.kwonlyargs
        except AttributeError: # py2, no kwonlyargs
            arg_list = arg_spec.args

        # check if number of guards makes sense
        if len(dargs) > len(arg_spec.args) or len(dkwargs) > len(arg_list):
            raise ValueError("Too many guard definitions for '%s()'" % decoratee.__name__)

        if len(dargs) == 1 and isinstance(dargs[0], RelGuard): # check if relguard is specified
            rel_guard = dargs[0]
            argument_guards = OrderedDict((arg, _) for arg in arg_spec.args) # might raise IndexError if empty
            _already_bound = () # UnboundLocalError emerges if this is not defined.
        elif len(dargs) == 1 and isinstance(dargs[0], types.FunctionType): # decorate directly (guards in annotations)
            rel_guard = _
            argument_guards = OrderedDict((arg, _) for arg in arg_spec.args) # might raise IndexError if empty
            _already_bound = () # UnboundLocalError emerges if this is not defined.
        else:
            rel_guard = _
            # bind positionals to their names
            argument_guards = OrderedDict(six.moves.zip_longest(arg_spec.args, dargs, fillvalue=_))
            _already_bound = arg_spec.args[:len(dargs)] # names of arguments matched with dargs

        for arg_name in dkwargs.keys():
            if arg_name in _already_bound: # check if guards in kwargs does not overlap with those bound above
                raise ValueError("Multiple definitions of guard for argument '%s'" % arg_name)
            if arg_name not in arg_list: # check if arg names are valid
                raise ValueError("Unexpected guard definition for not recognised argument '%s'" % arg_name)
        # no overlaps, so extend argument_guards:
        argument_guards.update(dkwargs)

        # if argument_guards is empty (catch-all, more precisely), try extracting guards from annotations
        if all(grd == _ for grd in argument_guards):
            try:
                arg_annotations = arg_spec.annotations # raises AttributeError in py2
                six.next(six.iterkeys(arg_annotations))
            except (AttributeError, # arg_spec was produced by getargspec (py2) thus we need to parse dargs'n'dkwargs
                    StopIteration): # or annotations are empty (py3)
                pass
            else:
                argument_guards = OrderedDict(
                        (arg_name, arg_annotations.get(arg_name, _)) # name -> annotation, or _ if no annotation.
                        for arg_name in arg_list # arg_list dictates right order
                        )
                try:
                    rel_guard = argument_guards.pop('return')
                except KeyError:
                    rel_guard = _ # FIXME: what about mixed definitions? e.g. guards as annotations, relguard as decarg?

        if (not argument_guards or all(grd is _ for grd in argument_guards)) and rel_guard is _:
            raise ValueError("No guards specified for '%s()'" % decoratee.__name__)

        # check if guards are really guards, or at least callable.
        if rel_guard is not _ and not isinstance(rel_guard, RelGuard):
            if strict_guard_definitions:
                raise ValueError("Specified relguard must be an instance of RelGuard, not %s" % type(rel_guard).__name__)
            else:
                if not callable(rel_guard):
                    raise ValueError("Specified relguard is not callable")
                warnings.warn("Specified relguard is not an instance of RelGuard. Its behaviour may be unexpected.",
                        RuntimeWarning)

        for arg_name, grd in argument_guards.items():
            if grd is not _ and not isinstance(grd, GuardFunc):
                if strict_guard_definitions:
                    raise ValueError("Guard specified for argument '%s' must be an instance of GuardFunc, not %s"
                            % (arg_name, type(grd).__name__))
                else:
                    if not callable(grd):
                        raise ValueError("Guard specified for argument '%s' is not callable" % arg_name)
                    warnings.warn("Guard specified for argument '%s' is not an instance of GuardFunc. Its behaviour may be unexpected."
                            % arg_name, RuntimeWarning)

        # check if relguard argument names fits with decoratee
        if isinstance(rel_guard, RelGuard): # only RelGuard objects have __argnames__ attr.
            for arg in rel_guard.__argnames__:
                if arg not in arg_spec.args and arg not in arg_spec.kwonlyargs:
                    raise ValueError("Relguard's argument names must be a subset of %s argument names" % decoratee.__name__)

        # check if defaults pass through guards
        if arg_spec.defaults is not None:
            argument_defaults = dict(
                    zip(
                        arg_spec.args[-len(arg_spec.defaults):], # slice of last elements. len(slice) == len(defaults)
                        arg_spec.defaults
                        )
                    )
        else:
            argument_defaults = dict()

        try:
            argument_defaults.update(dict(
                    zip(
                        arg_spec.kwonlyargs[-len(arg_spec.kwonlydefaults):],
                        arg_spec.kwonlydefaults
                        )
                    ))
        except AttributeError: # py2, no kwonlyargs
            pass

        for arg_name, def_val in argument_defaults.items():
            if argument_guards[arg_name](def_val) is False:
                raise ValueError("Default value for argument '%s' does not pass through a guard" % arg_name)

        argument_guards_list = list(argument_guards.values())

        @six.wraps(decoratee)
        def guarded(*args, **kwargs):

            # check relations between args/environment first
            bound_args = dict(zip(arg_spec.args[:len(args)], args)) # bind args to names
            bound_args.update(kwargs)
            if not rel_guard(**bound_args): # argument order in relguard is not guaranteed to match decoratee's
                raise GuardError("Arguments did not pass through relguard")

            # check input args one by one
            for i, arg_value in enumerate(args):
                grd = argument_guards_list[i]
                if not grd(arg_value):
                    raise GuardError("Wrong value for argument on position %i" % (i + 1))
                else:
                    pass # just to explicitly note, that argument passed guard.

            # then kwargs
            for arg_name, arg_value in kwargs.items():
                grd = argument_guards[arg_name]
                if not grd(arg_value):
                    raise GuardError("Wrong value for keyword argument '%s'" % arg_name)
                else:
                    pass # just to explicitly note, that argument passed guard.

            # TODO: relguard. after or before those ^ ?

            return decoratee(*args, **kwargs)

        ret = guarded
        ret._argument_guards = argument_guards
        ret._relguard = rel_guard
        ret.__guarded__ = decoratee # keep reference to original function (FIXME: needed?)
        return ret

    # decide whether initialise decorator
    if len(dkwargs) == 0 and len(dargs) == 1 and callable(dargs[0]) and not isinstance(dargs[0], (GuardFunc, RelGuard)):
        return decorator(dargs[0])
    else:
        return decorator

def rguard(rel_guard, **kwargs):
    return guard(RelGuard(rel_guard), **kwargs)
