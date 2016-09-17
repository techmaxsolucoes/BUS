#-*- coding: utf-8 -*-


# Given x instance of Expr and y anything
logical_ops = (
    ('Eq', '==', '__eq__'),  # x == y
    ('Ne', '!=', '__ne__'), # x != y
    ('Lt', '<', '__lt__'), # x < y
    ('Gt', '>', '__gt__'), # x > y
    ('Le', '<=', '__le__'), # x <= y
    ('Ge', '>=', '__ge__'), # x >= y
    ('And', '&', '__and__'), # x & y
    ('RAnd', '&', '__rand__'), # y & x
    ('Or', '|', '__or__'), # x | y
    ('ROr', '|', '__or__'), # y | x
    ('In', 'in', '__contains__'), # y in x
)

prefix_unary_logical_ops = (
    ('Not', 'not', '__not__'), # if not x
    ('Truth', 'truth', 'truth') # if x
)

infix_ops = (
    ('Add', '+', '__add__'), # x + y
    ('Iadd', '+=', '__iadd__'), # x += y
    ('RAdd', '+', '__radd__'), # y + x
    ('Concat', '+', '__concat__'), # str(x) + str(y)
    ('Sub', '-', '__sub__'), # x - y
    ('ISub', '-=', '__isub__'), # x -= y
    ('RSub', '-', '__rsub__'), # y - x
    ('Mul', '*', '__mul__'), # x * y
    ('IMul', '*=', '__imul__'), # x *= y
    ('RMul', '*', '__rmul__'), # y * x
    ('Div', '/', '__div__'), # x / y
    ('IDiv', '/=', '__idiv__'), # x /= y
    ('RDiv', '/', '__rdiv__'), # y / x
    ('Mod', '%', '__mod__'), # x % y
    ('RMod', '%', '__rmod__'), # y % x
    ('IMod', '%=', '__imod__'), # x %= y
    ('Pow', '**', '__pow__'), # x ** y
    ('RPow', '**', '__rpow__'), # y ** x
    ('IPow', '**', '__ipow__') # x **= y
)

prefix_unary_ops = (
    ('Not', 'not', '__invert__'), # ~x
    ('Pos', '+', '__pos__'), # +x
    ('Neg', '-', '__neg__'), # -y
)

postfix_unary_ops = (
    ('Is', 'is_', 'is_'), # x is y
    ('IsNot', 'is_not', 'is_not') # x is not y
)

binary_ops = logical_ops + infix_ops
unary_ops = prefix_unary_logical_ops + prefix_unary_ops + postfix_unary_ops
all_ops = prefix_unary_ops + postfix_unary_ops + binary_ops

class Expr(object):
    def __init__(self, value):
        self.value = value

    for cls, op, method in prefix_unary_ops + postfix_unary_ops:
        exec("""
        def {0}(self):
            return {1}(self, other)
        """.format(method, cls).strip())
    del cls, op, method

    for cls, op, method in binary_ops:
        exec("""
            def {0}(self, other):
                return {1}(self, other)
            """.format(method, cls).strip())
    del cls, op, method

    def __eq__(self, other):
        if other is None:
            return IsNone(self)
        return Eq(self, other)

    def __ne__(self, other):
        if other is None:
            return not IsNone(self)
        return Ne(self, other)

    def stack(self):
        if hasattr(self.value, 'stack'):
            return self.value.stack()
        return self.value


class Parenthesizing(object):
    pass


class PrefixUnaryOp(Expr, Parenthesizing):
    def stack(self):
        value = super(PrefixUnaryOp, self).stack()
        return (value, self._op)

class PostfixUnaryOp(Expr, Parenthesizing):
    def stack(self):
        value = super(PostfixUnaryOp, self).solve()
        return (value, self._op)

for cls, op, method in prefix_unary_ops:
    locals()[cls] = type(cls, (PrefixUnaryOp,), {"_op": op})
del cls, op, method

for cls, op, method in postfix_unary_ops:
    locals()[cls] = type(cls, (PostfixUnaryOp,), {"_op": op})
del cls, op, method

class BinaryOp(Expr, Parenthesizing):
    def __init__(self, left, right):
        self.left = left if isinstance(left, Expr) else Expr(left)
        self.right = right if isinstance(right, Expr) else Expr(right)

    def stack(self):
        left = self.left.stack()
        right = self.right.stack()
        return (left, self._op, right)

for cls, op, method in binary_ops:
    locals()[cls] = type(cls, (BinaryOp,), {"_op": op})
del cls, op, method
