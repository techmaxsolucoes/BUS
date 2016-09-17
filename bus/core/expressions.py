#-*- coding: utf-8 -*-

import numbers
import operator

binary_ops = (
    ('Eq', '=', '__eq__'),
    ('Ne', '!=', '__ne__'),
    ('Lt', '<', '__lt__'),
    ('Gt', '>', '__gt__'),
    ('Le', '<=', '__le__'),
    ('Ge', '>=', '__ge__'),
    ('And', 'and', '__and__'),
    ('Or', 'or', '__or__'),
    ('Add', '+', '__add__'),
    ('Sub', '-', '__sub__'),
    ('Mul', '*', '__mul__'),
    ('Div', '/', '__div__'),
    ('Mod', '%', '__mod__'),
    ('In', 'in', '__contains__'),
)

prefix_unary_ops = (
    ('Not', 'not', '__invert__'),
    ('Pos', '+', '__pos__'),
    ('Neg', '-', '__neg__'),
)

postfix_unary_ops = (
    ('Is', 'is_', 'is_'),
    ('IsNone', 'is_not', 'is_not')
)

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
