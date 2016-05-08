#TODO: test guards with default args
#TODO: write test for erroneous
import function_pattern_matching as fpm
import unittest
try:
    from test_fpm_py3 import *
    py3 = True
except SyntaxError:
    py3 = False

class DoGuardsWork(unittest.TestCase):
    def test_simple(self):
        "Test each basic guard"

        a1 = fpm.eq(10)
        self.assertTrue(a1(10))
        self.assertFalse(a1(0))

        a2 = fpm.ne(10)
        self.assertTrue(a2(11))
        self.assertFalse(a2(10))

        a3 = fpm.lt(10)
        self.assertTrue(a3(-100))
        self.assertFalse(a3(10))
        self.assertFalse(a3(9001)) # IT'S OVER 9000!!!

        a4 = fpm.le(10)
        self.assertTrue(a4(-100))
        self.assertTrue(a4(10))
        self.assertFalse(a4(100))

        a5 = fpm.gt(10)
        self.assertTrue(a5(11))
        self.assertFalse(a5(10))
        self.assertFalse(a5(9))

        a6 = fpm.ge(10)
        self.assertTrue(a6(11))
        self.assertTrue(a6(10))
        self.assertFalse(a6(9))

        a7 = fpm.Is(True)
        self.assertTrue(a7(True))
        self.assertFalse(a7(None))

        x_ = 1
        a7a = fpm.Is(x_)
        self.assertTrue(a7a(x_))
        self.assertFalse(a7a(2))

        a7b = fpm.Is(None)
        self.assertTrue(a7b(None))
        self.assertFalse(a7b(True))

        a8 = fpm.Isnot(None)
        self.assertTrue(a8(10))
        self.assertFalse(a8(None))

        a9 = fpm.isoftype(int)
        self.assertTrue(a9(10))
        self.assertFalse(a9('qwerty'))

        a10 = fpm.isiterable
        self.assertFalse(a10(10))
        self.assertTrue(a10("asd"))
        self.assertTrue(a10([1,2,3,4]))

        a11 = fpm.In(range(10))
        self.assertTrue(a11(5))
        self.assertFalse(a11(10))
        self.assertFalse(a11(15))

        a12 = fpm.notIn({'a', 2, False})
        self.assertTrue(a12(10))
        self.assertTrue(a12(True))
        self.assertFalse(a12('a'))
        self.assertFalse(a12(2))
        self.assertFalse(a12(False))

        a13 = fpm.eTrue
        self.assertTrue(a13(1))
        self.assertTrue(a13([10]))
        self.assertFalse(a13(0))
        self.assertFalse(a13([]))
        self.assertFalse(a13(''))

        a14 = fpm.eFalse
        self.assertFalse(a14(1))
        self.assertFalse(a14([10]))
        self.assertTrue(a14(0))
        self.assertTrue(a14([]))
        self.assertTrue(a14(''))

    def test_combined(self):
        "Test some combined guards"

        # is int and ((>0 and <=5) or =10)
        comp2 = fpm.isoftype(int) & ((fpm.gt(0) & fpm.le(5)) | fpm.eq(10))
        self.assertFalse(comp2(-10))
        self.assertFalse(comp2(0))
        self.assertTrue(comp2(1))
        self.assertTrue(comp2(4))
        self.assertTrue(comp2(5))
        self.assertFalse(comp2(6))
        self.assertTrue(comp2(10))
        self.assertFalse(comp2('a'))
        self.assertFalse(comp2([]))
        self.assertTrue(comp2(True)) # bool is subclass of int, meh

        # (is int and is not bool and >0 and <=5) or is None
        comp3 = (fpm.isoftype(int) & ~fpm.isoftype(bool) & fpm.gt(0) & fpm.le(5)) | fpm.Is(None)
        self.assertFalse(comp3(-10))
        self.assertFalse(comp3(0))
        self.assertTrue(comp3(1))
        self.assertTrue(comp3(4))
        self.assertTrue(comp3(5))
        self.assertFalse(comp3(6))
        self.assertFalse(comp3(10))
        self.assertFalse(comp3('a'))
        self.assertFalse(comp3([]))
        self.assertFalse(comp3(True))
        #self.assertTrue(comp3(None))

        # evals to True or is None
        comp4 = fpm.eTrue | fpm.Is(None)
        self.assertTrue(comp4(1))
        self.assertTrue(comp4(10))
        self.assertTrue(comp4('asd'))
        self.assertTrue(comp4({1,2,3}))
        self.assertFalse(comp4(0))
        self.assertFalse(comp4([]))
        self.assertFalse(comp4(''))
        self.assertFalse(comp4({}))
        self.assertFalse(comp4(set()))
        self.assertTrue(comp4(None))

        # is iterable xor evals to True
        comp5 = fpm.isiterable ^ fpm.eTrue
        self.assertTrue(comp5([]))
        self.assertTrue(comp5(1))
        self.assertFalse(comp5(0))
        self.assertFalse(comp5([1,2,3]))

    def test_relation_guards(self):
        "Test relguard (relations between arguments)"

        rg1 = fpm.relguard(lambda a, b, c: a + 1 == b and b + 1 == c and a > 0)
        self.assertTrue(rg1(a=1, b=2, c=3))
        self.assertFalse(rg1(a=0, b=0, c=0))
        self.assertFalse(rg1(a=[], b=0, c=0))
        self.assertEqual(rg1.__argnames__, {'a', 'b', 'c'})

        some_external_var = 9
        rg2 = fpm.relguard(lambda: some_external_var == 10)
        self.assertFalse(rg2())
        self.assertEqual(rg2.__argnames__, set())

    def test_guarded_correctly_decargs(self):
        "Test every possible correct way of defining guards (Py2 & 3, no relguards)"

        # positional all
        @fpm.guard(fpm.eq(0), fpm.gt(0), fpm.isoftype(int))
        def pc(a, b, c):
            return (a, b, c)

        self.assertEqual(pc(0, 1, 2), (0, 1, 2))
        self.assertRaises(fpm.GuardError, pc, 1, 1, 2)
        self.assertRaises(fpm.GuardError, pc, 0, -1, 2)
        self.assertRaises(fpm.GuardError, pc, 0, 1, 'a')
        self.assertRaises(fpm.GuardError, pc, 1, 1, 'a')

        # positional some (first two args)
        @fpm.guard(fpm.eTrue, fpm.eTrue & fpm.isiterable)
        def ps(a, b, c):
            return (a, b, c)

        self.assertEqual(ps(10, {1, 2}, None), (10, {1, 2}, None))
        self.assertEqual(ps(10, {1, 2}, fpm), (10, {1, 2}, fpm))
        self.assertRaises(fpm.GuardError, ps, None, [1], "x")
        self.assertRaises(fpm.GuardError, ps, 1, 1, "x")
        self.assertRaises(fpm.GuardError, ps, 1, [], "1")

        # positional first-only (a.k.a does it clash with relguard)
        @fpm.guard(~fpm.isiterable)
        def pfo(a, b, c):
            return (a, b, c)

        self.assertEqual(pfo(1, 0, 0), (1, 0, 0))
        self.assertRaises(fpm.GuardError, pfo, "string", None, None)

        # positional with catch-alls
        @fpm.guard(fpm._, fpm._, fpm.isoftype(float))
        def pwca1(a, b, c):
            return (a, b, c)

        self.assertEqual(pwca1(0, pwca1, 1.0), (0, pwca1, 1.0))
        self.assertRaises(fpm.GuardError, pwca1, 0, lambda: None, 9001)

        @fpm.guard(fpm.lt(0), fpm._, fpm.isoftype(float))
        def pwca2(a, b, c):
            return (a, b, c)

        self.assertEqual(pwca2(-1, (), 9000.1), (-1, (), 9000.1)) # that's over 9000, too.
        self.assertRaises(fpm.GuardError, pwca2, 0, 1, 1.0)
        self.assertRaises(fpm.GuardError, pwca2, -1, 1, 1)

        # keyword all
        @fpm.guard(
            a = fpm.ne(0),
            b = fpm.isoftype(str),
            c = fpm.eFalse
        )
        def ka(a, b, c):
            return (a, b, c)

        self.assertEqual(ka(1, "", ""), (1, "", ""))
        self.assertRaises(fpm.GuardError, ka, 0, "", [])
        self.assertRaises(fpm.GuardError, ka, 1, 1, 0)
        self.assertRaises(fpm.GuardError, ka, 1, '', True)

        # keyword some
        @fpm.guard(
            a = fpm.Isnot(None),
            c = fpm.In(range(100))
        )
        def ks(a, b, c):
            return (a, b, c)

        self.assertEqual(ks(True, 0, 50), (True, 0, 50))
        self.assertRaises(fpm.GuardError, ks, None, 0, 50)
        self.assertRaises(fpm.GuardError, ks, 1, '', 1000)

    def test_guarded_correctly_decargs_with_relguards(self):
        "Test every possible correct way of defining guards (Py2 & 3, with relguards)"

        # relguard-only all
        @fpm.guard(
            fpm.relguard(lambda a, b, c: a == b and b < c)
        )
        def roa(a, b, c):
            return (a, b, c)

        self.assertEqual(roa(10, 10, 15), (10, 10, 15))
        self.assertRaises(fpm.GuardError, roa, 1, 5, 12)
        self.assertRaises(fpm.GuardError, roa, 1, 1, -5)
        self.assertRaises(fpm.GuardError, roa, [], [], 0)

        # relguard-only some
        @fpm.guard(
            fpm.relguard(lambda a, c: (a + 1) == c)
        )
        def ros(a, b, c):
            return (a, b, c)

        self.assertEqual(ros(10, -10, 11), (10, -10, 11))
        self.assertRaises(fpm.GuardError, ros, 0, 0, 0)

        # relguard-only none
        some_external_var = True
        @fpm.guard(
            fpm.relguard(lambda: some_external_var == True)
        )
        def ron(a, b, c):
            return (a, b, c)

        self.assertEqual(ron(1, 1, 1), (1, 1, 1))
        some_external_var = False
        self.assertRaises(fpm.GuardError, ron, 1, 1, 1)

        # relguard with all keywords
        @fpm.guard(
            fpm.relguard(lambda a, c: a == c),
            a = fpm.isoftype(int),
            b = fpm.isoftype(str),
            c = fpm.isoftype(float)
        )
        def rwak(a, b, c):
            return (a, b, c)

        self.assertEqual(rwak(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwak, 9000, "x", 9000.1)
        self.assertRaises(fpm.GuardError, rwak, 'x', 'y', 'x')
        self.assertRaises(fpm.GuardError, rwak, 1, 0, 1.0)
        self.assertRaises(fpm.GuardError, rwak, 1, 'x', 1)

        # relguard with some keywords
        @fpm.guard(
            fpm.relguard(lambda a, c: a == c),
            a = fpm.isoftype(int)
        )
        def rwsk(a, b, c):
            return (a, b, c)

        self.assertEqual(rwsk(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwsk, 9000, "x", 9000.1)
        self.assertRaises(fpm.GuardError, rwsk, 'x', 'y', 'x')

    def test_rguard_decargs(self):
        "Test every possible correct way of defining guards with rguard decorator (Py2 & 3)"

        # relguard-only all
        @fpm.rguard(lambda a, b, c: a == b and b < c)
        def roaR(a, b, c):
            return (a, b, c)

        self.assertEqual(roaR(10, 10, 15), (10, 10, 15))
        self.assertRaises(fpm.GuardError, roaR, 1, 5, 12)
        self.assertRaises(fpm.GuardError, roaR, 1, 1, -5)
        self.assertRaises(fpm.GuardError, roaR, [], [], 0)

        # relguard-only some
        @fpm.rguard(lambda a, c: (a + 1) == c)
        def rosR(a, b, c):
            return (a, b, c)

        self.assertEqual(rosR(10, -10, 11), (10, -10, 11))
        self.assertRaises(fpm.GuardError, rosR, 0, 0, 0)

        # relguard-only none
        some_external_var = True
        @fpm.rguard(lambda: some_external_var == True)
        def ronR(a, b, c):
            return (a, b, c)

        self.assertEqual(ronR(1, 1, 1), (1, 1, 1))
        some_external_var = False
        self.assertRaises(fpm.GuardError, ronR, 1, 1, 1)

        # relguard with all keywords
        @fpm.rguard(
            lambda a, c: a == c,
            a = fpm.isoftype(int),
            b = fpm.isoftype(str),
            c = fpm.isoftype(float)
        )
        def rwakR(a, b, c):
            return (a, b, c)

        self.assertEqual(rwakR(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwakR, 9000, "x", 9000.1)
        self.assertRaises(fpm.GuardError, rwakR, 'x', 'y', 'x')
        self.assertRaises(fpm.GuardError, rwakR, 1, 0, 1.0)
        self.assertRaises(fpm.GuardError, rwakR, 1, 'x', 1)

        # relguard with some keywords
        @fpm.rguard(
            lambda a, c: a == c,
            a = fpm.isoftype(int)
        )
        def rwskR(a, b, c):
            return (a, b, c)

        self.assertEqual(rwskR(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwskR, 9000, "x", 9000.1)
        self.assertRaises(fpm.GuardError, rwskR, 'x', 'y', 'x')

    def test_guarded_correctly_annotations(self):
        "Test every possible correct way of defining guards as annotations (Py3 only, no relguards)"

        if not py3:
            return

        # annotations all
        self.assertEqual(ka3(1, "", ""), (1, "", ""))
        self.assertRaises(fpm.GuardError, ka3, 0, "", [])
        self.assertRaises(fpm.GuardError, ka3, 1, 1, 0)
        self.assertRaises(fpm.GuardError, ka3, 1, '', True)

        # annotations some
        self.assertEqual(ks3(True, 0, 50), (True, 0, 50))
        self.assertRaises(fpm.GuardError, ks3, None, 0, 50)
        self.assertRaises(fpm.GuardError, ks3, 1, '', 1000)

    def test_guarded_correctly_annotations_with_relguards(self):
        "Test every possible correct way of defining guards as annotations (Py3 only, with relguards)"

        if not py3:
            return

        # relguard-only all
        self.assertEqual(roa3(10, 10, 15), (10, 10, 15))
        self.assertRaises(fpm.GuardError, roa3, 1, 5, 12)
        self.assertRaises(fpm.GuardError, roa3, 1, 1, -5)
        self.assertRaises(fpm.GuardError, roa3, [], [], 0)

        # relguard-only some
        self.assertEqual(ros3(10, -10, 11), (10, -10, 11))
        self.assertRaises(fpm.GuardError, ros3, 0, 0, 0)

        # relguard-only none
        some_external_var3 = True
        self.assertEqual(ron3(1, 1, 1), (1, 1, 1))
        #some_external_var3 = False
        #self.assertRaises(fpm.GuardError, ron3, 1, 1, 1)

        # relguard with all annotations
        self.assertEqual(rwak3(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwak3, 9000, "x", 9000.1)
        self.assertRaises(fpm.GuardError, rwak3, 'x', 'y', 'x')
        self.assertRaises(fpm.GuardError, rwak3, 1, 0, 1.0)
        self.assertRaises(fpm.GuardError, rwak3, 1, 'x', 1)

        # relguard with some annotations
        self.assertEqual(rwsk3(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwsk3, 9000, "x", 9000.1)
        self.assertRaises(fpm.GuardError, rwak3, 'x', 'y', 'x')

        # relguard with all annotations, mixed
        self.assertEqual(rwak3m(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwak3m, 9000, "x", 9000.1)
        self.assertRaises(fpm.GuardError, rwak3m, 'x', 'y', 'x')
        self.assertRaises(fpm.GuardError, rwak3m, 1, 0, 1.0)
        self.assertRaises(fpm.GuardError, rwak3m, 1, 'x', 1)

        # relguard with some annotations, mixed
        self.assertEqual(rwsk3m(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwsk3m, 9000, "x", 9000.1)
        self.assertRaises(fpm.GuardError, rwak3m, 'x', 'y', 'x')

    def test_rguard_annotations(self):
        "Test every possible correct way of defining guards with rguard decorator (Py3 only)"

        if not py3:
            return

        # relguard with all annotations, rguard mixed
        self.assertEqual(rwak3rm(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwak3rm, 9000, "x", 9000.1)

        # relguard with some annotations, rguard mixed
        self.assertEqual(rwsk3rm(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwsk3rm, 9000, "x", 9000.1)

    def test_raguard_annotations(self):
        "Test raguard"

        if not py3:
            return

        # relguard-only all
        self.assertEqual(roa3ra(10, 10, 15), (10, 10, 15))
        self.assertRaises(fpm.GuardError, roa3ra, 1, 5, 12)
        self.assertRaises(fpm.GuardError, roa3ra, 1, 1, -5)
        self.assertRaises(fpm.GuardError, roa3ra, [], [], 0)

        # relguard-only some
        self.assertEqual(ros3ra(10, -10, 11), (10, -10, 11))
        self.assertRaises(fpm.GuardError, ros3ra, 0, 0, 0)

        # relguard-only none
        self.assertEqual(ron3ra(1, 1, 1), (1, 1, 1))
        #self.assertRaises(fpm.GuardError, ron3ra, 1, 1, 1)

        # relguard with all annotations
        self.assertEqual(rwak3ra(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwak3ra, 9000, "x", 9000.1)
        self.assertRaises(fpm.GuardError, rwak3ra, 'x', 'y', 'x')
        self.assertRaises(fpm.GuardError, rwak3ra, 1, 0, 1.0)
        self.assertRaises(fpm.GuardError, rwak3ra, 1, 'x', 1)

        # relguard with some annotations
        self.assertEqual(rwsk3ra(1, "asd", 1.0), (1, "asd", 1.0))
        self.assertRaises(fpm.GuardError, rwsk3ra, 9000, "x", 9000.1)
        self.assertRaises(fpm.GuardError, rwak3ra, 'x', 'y', 'x')

    def test_guarded_definition_errors_decargs(self):
        "Test syntactically correct but erroneous guard definitions"

        ## no relguard tests:

        # no guards

        # too many positionals

        # not known keyword arg

        # positional-keyword overlap (same)

        # positional-keyword overlap (diff)

        # not a guard

        ## with relguard tests:

        # not a relguard

        # wrong arg names in relguard

        # exceeding arg names in relguard (good mixed with bad)

        # relguard with positionals

        # relguard with positionals as not 1st arg

        # defaults not passing through guards and relguard

        # guarding guarded
        pass

    def test_guarded_definition_errors_annotations(self):
        "Test syntactically correct but erroneous guard definitions"
        pass

class IsDispatchCorrect():#unittest.TestCase):
    def test_with_catchall(self):
        "Test function defined with catch all case"

        @fpm.case
        def foo(a='bar', b=1337, c=(0, 1, 2)):
            return "str:bar, int:1337, tuple:(0, 1, 2)"

        @fpm.case
        def foo(a='baz', b=1337, c=(0, 1, 2)):
            return "str:baz, int:1337, tuple:(0, 1, 2)"

        @fpm.case
        def foo(a, b=1331, c=(0, 1, 2)):
            return "any, int:1331, tuple:(0, 1, 2)"

        @fpm.case
        def foo(a, b, c='baz'):
            return "any, any, str:baz"

        @fpm.case(1, fpm._, fpm._) # equivalent, needed, when we want to match before non-default arg.
        def foo(a, b, c):
            return "int:1, any, any"

        @fpm.case
        def foo(a, b, c):
            return "any, any, any"

        @fpm.case
        def foo(a, b, c, d): #different arity, but is that an issue?
            return "any, any, any, any"

        self.assertEqual(foo('bar', 1337, (0, 1, 2)), "str:bar, int:1337, tuple:(0, 1, 2)")
        self.assertEqual(foo('baz', 1337, (0, 1, 2)), "str:baz, int:1337, tuple:(0, 1, 2)")
        self.assertEqual(foo('xyz', 1337, (0, 1, 2)), "any, any, any")
        self.assertEqual(foo('xyz', 1331, (0, 1, 2)), "any, int:1331, tuple:(0, 1, 2)")
        self.assertEqual(foo(1, dict(), False), "int:1, any, any")
        self.assertEqual(foo('xyz', 1237, (0, 1, 2)), "any, any, any")
        self.assertEqual(foo('xyz', 1237, 'baz'), "any, any, str:baz")
        self.assertEqual(foo('bar', 1337, (0, 1, 2), True), "any, any, any, any")

    def test_factorial(self):
        "Erlang-like factorial"

        # no accumulator, because this is just for a testing sake, not performance.

        @fpm.case
        def fac(n=0):
            return 1

        @fpm.case
        @fpm.guard(fpm.ge(0) & fpm.is_int)
        def fac(n):
            return n * fac(n-1)

        self.assertRaises(fpm.GuardError, fac, -1)
        self.assertRaises(fpm.GuardError, fac, 'not an int')

        self.assertEqual(fac(0), 1)
        self.assertEqual(fac(1), 1)
        self.assertEqual(fac(2), 2)
        self.assertEqual(fac(3), 6)

        self.assertEqual(fac(7), 5040)
        self.assertEqual(fac(8), 40320)
        self.assertEqual(fac(9), 362880)


    def test_fibonacci(self):
        "Erlang-like fibonacci"

        # no accumulator, because this is just for a testing sake, not performance.

        @fpm.case
        def fib(n=0):
            return 0

        @fpm.case
        def fib(n=1):
            return 1

        @fpm.case
        @fpm.guard(fpm.ge(0))
        def fib(n):
            return fib(n-1) + fib(n-2)

        self.assertRaises(fpm.GuardError, fib, -1)

        self.assertEqual(fib(0), 0)
        self.assertEqual(fib(1), 1)
        self.assertEqual(fib(2), 1)

        self.assertEqual(fib(8), 21)
        self.assertEqual(fib(9), 34)
        self.assertEqual(fib(10), 55)
        self.assertEqual(fib(11), 89)

if __name__ == '__main__':
    unittest.main()
