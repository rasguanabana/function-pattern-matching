#TODO: test guards with default args
#TODO: write test for erroneous
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import function_pattern_matching as fpm
import unittest
try:
    from py3_defs import *
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

        a9b = fpm.isoftype(int, float)
        self.assertTrue(a9b(10))
        self.assertTrue(a9b(10.5))
        self.assertFalse(a9b('x'))

        a9c = fpm.isoftype((int, float))
        self.assertTrue(a9c(10))
        self.assertTrue(a9c(10.5))
        self.assertFalse(a9c('x'))

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

        # fancy, with default args
        @fpm.guard(
            fpm.relguard(lambda a, c: type(a) == type(c)),
            a = fpm.eTrue,
            b = fpm.Isnot(None)
        )
        def fancy(a, b=[], c=1):
            return (a, b, c)

        self.assertEqual(fancy(9), (9, [], 1))
        self.assertEqual(fancy(-1, 'x'), (-1, 'x', 1))
        self.assertEqual(fancy('a', b'b', 'c'), ('a', b'b', 'c'))

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

        # annotations + default values
        self.assertEqual(ad3(2), (2, True, None))
        self.assertEqual(ad3(2, False), (2, False, None))
        self.assertEqual(ad3(2, c=10), (2, True, 10))
        self.assertEqual(ad3(2, False, 11), (2, False, 11))
        self.assertRaises(fpm.GuardError, ad3, 2.0)
        self.assertRaises(fpm.GuardError, ad3, 1, [])
        self.assertRaises(fpm.GuardError, ad3, 1, False, -1)

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

        def decoratee_basic(a, b, c):
            return (a, b, c)
        ## no relguard tests:

        # no guards
        self.assertRaises(ValueError, fpm.guard, decoratee_basic) # @guard
        self.assertRaises(ValueError, fpm.guard(), decoratee_basic) # @guard()

        # too many positionals
        self.assertRaises(ValueError, fpm.guard(fpm.eTrue, fpm.eTrue, fpm.eTrue, fpm.eTrue), decoratee_basic) # @guard(....)

        # not known keyword arg
        self.assertRaises(ValueError, fpm.guard(d=fpm.eTrue), decoratee_basic)

        # positional-keyword overlap (same)
        self.assertRaises(ValueError, fpm.guard(fpm.eFalse, fpm.eFalse, a=fpm.eFalse), decoratee_basic)
        self.assertRaises(ValueError, fpm.guard(fpm.eFalse, a=fpm.eFalse), decoratee_basic)

        # positional-keyword overlap (diff)
        self.assertRaises(ValueError, fpm.guard(fpm.eTrue, fpm.eFalse, a=fpm.eFalse), decoratee_basic)
        self.assertRaises(ValueError, fpm.guard(fpm.eTrue, a=fpm.eFalse), decoratee_basic)

        # not a guard
        self.assertRaises(ValueError, fpm.guard(zip, list, all), decoratee_basic)

        ## with relguard tests:

        # not a relguard
        try:
            fpm.guard(lambda a, b, c: a and b and c)(decoratee_basic)
        except ValueError:
            pass
        else:
            self.fail("Expected ValueError")

        # wrong arg names in relguard
        self.assertRaises(ValueError, fpm.guard(fpm.relguard(lambda a, v, x: a and v and x)), decoratee_basic)

        # exceeding arg names in relguard (good mixed with bad)
        self.assertRaises(ValueError, fpm.guard(fpm.relguard(lambda a, b, c, x: a and b and c and x)), decoratee_basic)

        # relguard mixed with positionals
        self.assertRaises(ValueError, fpm.guard(fpm.relguard(lambda: True), fpm.eq(0), fpm.eFalse, fpm.eFalse), decoratee_basic)

        # relguard with positionals as not 1st arg
        self.assertRaises(ValueError, fpm.guard(fpm.eq(0), fpm.relguard(lambda: True), fpm.eFalse, fpm.eFalse), decoratee_basic)

        # defaults not passing through guards and relguard
        #def decoratee_defaults(a, b=10, c=0):
        #    return (a, b, c)

        #assertRaises(ValueError, fpm.guard(fpm._, fpm.gt(100), fpm.eTrue)(decoratee_defaults))

        # var (kw)args
        def decoratee_var1(*args):
            return args
        self.assertRaises(ValueError, fpm.guard(fpm.eTrue), decoratee_var1)

        def decoratee_var2(a, *args):
            return (a, args)
        self.assertRaises(ValueError, fpm.guard(args=fpm.eTrue), decoratee_var2)

        def decoratee_var3(**kwargs):
            return kwargs
        self.assertRaises(ValueError, fpm.guard(kwargs=fpm.eTrue), decoratee_var3)

        def decoratee_var4(a, b, *args, **kwargs):
            return (a, b, args, kwargs)
        self.assertRaises(ValueError, fpm.guard(fpm.eTrue, fpm.eTrue, fpm.eTrue, fpm.eTrue), decoratee_var4)

        # guarding guarded
        @fpm.guard(fpm.ne(0))
        def already_guarded(a):
            return a
        self.assertRaises(ValueError, fpm.guard(fpm.eTrue), already_guarded)

        if py3:
            # raguard, no return annotation
            def nra(): pass
            self.assertRaises(ValueError, fpm.raguard, nra)

            # not erroneous, but annotations should be ignored if decorator arguments are specified
            da_with_ann = fpm.guard(fpm.relguard(lambda a, c: a != c), a=~fpm.isoftype(int), b=~fpm.isoftype(str))(rwak3_bare)
            self.assertRaises(fpm.GuardError, da_with_ann, 1, 'x', 1)
            self.assertRaises(fpm.GuardError, da_with_ann, 1, 'x', 2)
            self.assertRaises(fpm.GuardError, da_with_ann, 'x', 'y', 2)
            self.assertEqual(da_with_ann('x', [], 2), ('x', [], 2))
            self.assertIs(da_with_ann._argument_guards['c'], fpm._)

class IsDispatchCorrect(unittest.TestCase):
    def test_with_catchall(self):
        "Test function defined with catch all case"

        # all defaults
        @fpm.case
        def foo(a='bar', b=1337, c=(0, 1, 2)):
            return (1, a, b, c)

        @fpm.case
        def foo(a='baz', b=1337, c=(0, 1, 2)):
            return (2, a, b, c)

        # some defaults
        @fpm.case
        def foo(a, b=1331, c=(0, 1, 2)):
            return (3, a, b, c)

        @fpm.case
        def foo(a, b, c='baz'):
            return (4, a, b, c)

        # decorator args, some
        @fpm.case(1, fpm._, fpm._)
        def foo(a, b, c):
            return (5, a, b, c)

        # _ in defaults
        @fpm.case
        def foo(a=fpm._, b=2, c=fpm._):
            return (6, a, b, c)

        # any/3
        @fpm.case
        def foo(a, b, c):
            return (7, a, b, c)

        # any/4
        @fpm.case
        def foo(a, b, c, d): #different arity, but is that an issue?
            return (8, a, b, c, d)

        self.assertEqual(foo('bar', 1337, (0, 1, 2)),       (1, 'bar', 1337, (0, 1, 2)))
        self.assertEqual(foo('baz', 1337, (0, 1, 2)),       (2, 'baz', 1337, (0, 1, 2)))
        self.assertEqual(foo('xyz', 1331, (0, 1, 2)),       (3, 'xyz', 1331, (0, 1, 2)))
        self.assertEqual(foo('xyz', 1237, 'baz'),           (4, 'xyz', 1237, 'baz'))
        self.assertEqual(foo(1, dict(), False),             (5, 1, dict(), False))
        self.assertEqual(foo([], 2, b''),                   (6, [], 2, b''))
        self.assertEqual(foo('xyz', 1337, (0, 1, 2)),       (7, 'xyz', 1337, (0, 1, 2)))
        self.assertEqual(foo('xyz', 1237, (0, 1, 2)),       (7, 'xyz', 1237, (0, 1, 2)))
        self.assertEqual(foo('bar', 1337, (0, 1, 2), True), (8, 'bar', 1337, (0, 1, 2), True))

    def test_factorial(self):
        "Erlang-like factorial"

        # no accumulator, because this is just for a testing, not performance.

        @fpm.case
        def fac(n=0):
            return 1

        @fpm.case
        @fpm.guard(fpm.ge(0) & fpm.isoftype(int))
        def fac(n):
            return n * fac(n-1)

        self.assertRaises(fpm.MatchError, fac, -1)
        self.assertRaises(fpm.MatchError, fac, 'not an int')

        self.assertEqual(fac(0), 1)
        self.assertEqual(fac(1), 1)
        self.assertEqual(fac(2), 2)
        self.assertEqual(fac(3), 6)

        self.assertEqual(fac(7), 5040)
        self.assertEqual(fac(8), 40320)
        self.assertEqual(fac(9), 362880)


    def test_fibonacci(self):
        "Erlang-like fibonacci"

        # no accumulator, because this is just for a testing, not performance.

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

        self.assertRaises(fpm.MatchError, fib, -1)

        self.assertEqual(fib(0), 0)
        self.assertEqual(fib(1), 1)
        self.assertEqual(fib(2), 1)

        self.assertEqual(fib(8), 21)
        self.assertEqual(fib(9), 34)
        self.assertEqual(fib(10), 55)
        self.assertEqual(fib(11), 89)

    def test_bad_case_defs(self):
        "Syntactically correct, but erroneous multi-clause functions definitions."

        # varargs
        def varargs(a, b, *c):
            return (1, a, b, c)

        self.assertRaises(ValueError, fpm.case(1, 2, ()), varargs)

        def varargs(a, b, **c):
            return (2, a, b, c)

        self.assertRaises(ValueError, fpm.case(1, 2, {}), varargs)

        # kwonly
        if py3:
            self.assertRaises(ValueError, fpm.case(a=1, b=2, c=3), kwonly)

        # decorator args and defaults
        def decdef(a=1, b=2, c=3):
            return (3, a, b, c)

        self.assertRaises(ValueError, fpm.case(1, 2, 3), decdef)

        # exceeding positionals
        def regular (a, b, c):
            return (4, a, b, c)

        self.assertRaises(ValueError, fpm.case(1, 2, 3, 4), regular)

        # arg name mismatch
        self.assertRaises(ValueError, fpm.case(c=3, d=0), regular)

    def test_dispatch(self):
        "Test dispatch decorator" # TODO: improve test

        @fpm.dispatch(int, float, str)
        def dis(a, b, c):
            return (1, a, b, c)

        @fpm.dispatch(int, fpm._, int)
        def dis(a, b, c):
            return (2, a, b, c)

        @fpm.dispatch
        def dis(a=str, b=str, c=str):
            return(3, a, b, c)

        self.assertEqual(dis(1, 2.0, '3'),      (1, 1, 2.0, '3'))
        self.assertEqual(dis(1, b'', 3),        (2, 1, b'', 3))
        self.assertEqual(dis('1', '2', '3'),    (3, '1', '2', '3'))
        self.assertRaises(fpm.MatchError, dis, '1', [], 0)

if __name__ == '__main__':
    unittest.main()
