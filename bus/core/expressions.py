#-*- coding: utf-8 -*-

# Given x instance of Expr and y anything

logical_ops = (
    ('Eq', '=', '__eq__'),  # x == y
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
    ('Truth', 'truth', 'truth') # if x is True
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


def with_metaclass(meta, base=object):
    return meta('NewBase', (base,), {})


class Value(object)
    """Base class to store a value """
    def __init__(self, value):
        self.value

    def stack(self):
        return self.value

    def __repr__(self):
        return "<{}: ({})>".format(self.__class__.__name__, self.value)


class LogicalMetaClass(type):
    """Meta class to automatic creation of logical operators"""
    def __new__(cls, name, base, attrs):

        for cls_name, op_symbol, op_attr in prefix_unary_logical_ops:
            def fn(self):
                return globals()[cls_name](self)
            attrs[op_attr] = fn
        del cls_name, op_symbol, op_attr

        for cls_name, op_symbol, op_attr in postfix_unary_ops:
            def fn(self):
                return globals()[cls_name](self)
            attrs[op_attr] = fn
        del cls_name, op_symbol, op_attr

        for cls_name, op_symbol, op_attr in logical_ops:
            def fn(self, other):
                return globals()[cls_name](self, other)
            attrs[op_attr] = fn
        del cls_name, op_symbol, op_attr

        return type.__new__(cls, name, bases, attrs)


class Logical(with_metaclass(LogicalMetaClass, Value)):
    """A class that encapsulate the operators required to do any logical operation"""


class InfixMetaClass(type):
    """Meta class to automatic creation of infix operators"""
    def __new__(cls, name, bases, attrs):

        for cls_name, op_symbol, op_attr in prefix_unary_ops:
            def fn(self):
                return globals()[cls_name](self)
            attrs[op_attr] = fn
        del cls_name, op_symbol, op_attr

        for cls_name, op_symbol, op_attr in infix_ops:
            def fn(self, other):
                return globals()[cls_name](self, other)
            attrs[op_attr] = fn
        del cls_name, op_symbol, op_attr

        return type.__new__(cls, name, bases, attrs)


class Infix(with_metaclass(InfixMetaClass, Value)):
    """A class that encapsulate the operators to do any math operation"""


class Expr(Logical, Infix):
    """A class that encapsulate the math operators and logical operators"""
    def __eq__(self, other):
        if other is None:
            return Is(self, other)
        else:
            return Eq(self, other)

    def __ne__(self, other):
        if other is None:
            return IsNot(self, other)
        else:
            return Eq(self, other)

    def stack(self):
        if hasattr(self.value, 'stack'):
            return self.value.stack()
        return self.value


class Parenthesizing(object):
    """Base class to indicate a parenthesizing""""


class PrefixUnaryOp(Expr, Parenthesizing):
    """Base class to all prefixed unary operators"""
    def stack(self):
        value = super(PrefixUnaryOp, self).stack()
        return (self._op, value)

    def __repr__(self):
        return "<{}: ({} {})>".format(
            self.__class__.__name__,
            self._op,
            super(PrefixUnaryOp, self).stack())


class PostfixUnaryOp(Expr, Parenthesizing):
    """Base class to all postfixed unary operators"""
    def stack(self):
        value = super(PostfixUnaryOp, self).solve()
        return (value, self._op)

    def __repr__(self):
        return "<{}: ({} {})>".format(
            self.__class__.__name__,
            super(PostfixUnaryOp, self).stack(),
            self._op)


for cls_name, op_symbol, op_attr in prefix_unary_ops:
    locals()[cls_name] = type(cls_name, (PrefixUnaryOp,), {"_op": op_symbol})
del cls_name, op_symbol, op_attr


for cls_name, op_symbol, op_attr in postfix_unary_ops:
    locals()[cls_name] = type(cls_name, (PostfixUnaryOp,), {"_op": op_symbol})
del cls_name, op_symbol, op_attr


class BinaryOp(Expr, Parenthesizing):
    """Base class to all binary operators"""
    def __init__(self, left, right):
        self.left = left if isinstance(left, Expr) else Expr(left)
        self.right = right if isinstance(right, Expr) else Expr(right)

    def stack(self):
        left = self.left.stack()
        right = self.right.stack()
        return (left, self._op, right)

    def __repr__(self):
        return "<{}: ({} {} {})>".format(
            self.__class__.__name__,
            self.left.stack(),
            self._op,
            self.right.stack())


for cls_name, op_symbol, op_attr in postfix_unary_ops:
    locals()[BinaryOp] = type(cls_name, (PostfixUnaryOp,), {"_op": op_symbol})
del cls_name, op_symbol, op_attr
