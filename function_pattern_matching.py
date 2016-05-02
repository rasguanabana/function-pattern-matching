from collections import defaultdict
import inspect

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


class Multi_function():
    def __init__(self):
        self.functions = list()

    @staticmethod
    def __ismatching(arg_tuple, function_head):
        pass

    def __call__(self, *args):
        # returns first matching head:
        function_body = next(
                (f.body for f in self.functions if __ismatching(args, f.head)), # generator finds only matching heads
                lambda: raise MatchError # default value, when next() hit StopIteration (generator was empty)
                )                        # so when no match was found, MatchError is raised.
        return function_body(*args) # execute and return result.

    def append(self, *):
        pass


_ = _() # we need just one and only one instance.

function_refs = defaultdict(lambda: defaultdict(Multi_function)) # needed for case to track multi-headed functions.
    # module name -> fun qualname -> Multi_function object

def case(*args):
    "Main wrapper. *args can be pattern to match against, or directly a function head."

    def decorator(decoratee, pattern=None):
        "Actual decorator. Registers function head (pattern) and corresponding function body."

        # TODO: many try's to keep compat with py2.
        # needed:
        # - extract pattern from (case *args)/(fun arg defaults)/annotations
        # then:
        # - function_refs[module][fun_name].append(pattern, body), if no errors/exceptions.

        return dispatcher
