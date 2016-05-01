import function_pattern_matching as fpm
import unittest

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
