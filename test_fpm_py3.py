# annotations all
@fpm.guard
def ka3(
    a: fpm.ne(0),
    b: fpm.isoftype(str),
    c: fpm.eFalse
):
    return (a, b, c)

# annotations some
@fpm.guard
def ks3(
    a: fpm.Isnot(None),
    b, # implicit _
    c: fpm.In(range(100))
):
    return (a, b, c)

# relguard-only all
@fpm.guard
def roa3(a, b, c) -> fpm.relguard(lambda a, b, c: a == b and b > c):
    return (a, b, c)

# relguard-only some
@fpm.guard
def ros3(a, b, c) -> fpm.relguard(lambda a, c: (a + 1) == c):
    return (a, b, c)

# relguard-only none
@fpm.guard
def ron3(a, b, c) -> fpm.relguard(lambda: bool(10) == True):
    return (a, b, c)

# relguard with all annotations
@fpm.guard
def rwak3(
    a: fpm.isoftype(int),
    b: fpm.isoftype(str),
    c: fpm.isoftype(float)
) -> fpm.relguard(lambda a, c: a == c):
    return (a, b, c)

# relguard with some annotations
@fpm.guard
def rwsk3(
    a: fpm.isoftype(int),
    b,
    c
) -> fpm.relguard(lambda a, c: a == c):
    return (a, b, c)

# relguard with all annotations, mixed
@fpm.guard(
    fpm.relguard(lambda a, c: a == c)
)
def rwak3m(
    a: fpm.isoftype(int),
    b: fpm.isoftype(str),
    c: fpm.isoftype(float)
):
    return (a, b, c)

# relguard with some annotations, mixed
@fpm.guard(
    fpm.relguard(lambda a, c: a == c)
)
def rwsk3m(
    a: fpm.isoftype(int),
    b,
    c
):
    return (a, b, c)
