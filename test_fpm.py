import function_pattern_matching as fpm
import unittest

class DoesGuardsWork(unittest.TestCase):
    def test_simple(self):
        "Test each simple guard"

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
        "Test relguard (relations between arguments"

        # ABC + A*~B~(~A*~C) <=> A(C + ~B)
        # ...
        raise NotImplementedError

class IsDispatchCorrect(unittest.TestCase):
    def test_with_catchall(self):
        "Test function defined with catch all case."

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
        "Erlang-like factorial."

        # no accumulator, because this is just for a testing sake, not performance.

        @fpm.case
        def fac(n=0):
            return 1

        @fpm.case
        @fpm.guard( (fpm.ge(0), fpm.is_int) )
        def fac(n):
            return n * fac(n-1)

        self.assertRaises(fpm.GuardError, fac, (-1,))
        self.assertRaises(fpm.GuardError, fac, ('not an int',))

        self.assertEqual(fac(0), 1)
        self.assertEqual(fac(1), 1)
        self.assertEqual(fac(2), 2)
        self.assertEqual(fac(3), 6)

        self.assertEqual(fac(7), 5040)
        self.assertEqual(fac(8), 40320)
        self.assertEqual(fac(9), 362880)


    def test_fibonacci(self):
        "Erlang-like fibonacci."

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

        self.assertRaises(fpm.GuardError, fib, (-1,))

        self.assertEqual(fib(0), 0)
        self.assertEqual(fib(1), 1)
        self.assertEqual(fib(2), 1)

        self.assertEqual(fib(8), 21)
        self.assertEqual(fib(9), 34)
        self.assertEqual(fib(10), 55)
        self.assertEqual(fib(11), 89)

if __name__ == '__main__':
    unittest.main()
