#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import uuid
import copy
from registry import registry


class attrdict(dict):
    #: like a dictionary except `obj.foo` can be used in addition to `obj['foo']`
    #, and setting obj.foo = None deletes item foo

    __slots__ = ()
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __getitem__ = dict.get

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return self.get(attr, None)

    __repr__ = lambda self: '<adict {}>'.format(dict.__repr__(self))
    __getstate__ = lambda self: None
    __copy__ = lambda self: attrdict(self)
    __deepcopy__ = lambda self, memo: attrdict(copy.deepcopy(dict(self)))


class Status:
    STARTING = 1
    STOPPING = 2
    RUNNING = 3
    STOPPED = 4


class ComponentMetaClass(type):
    def __init__(cls, name, bases, attrs):
        registry.register(cls)


def with_metaclass(meta, base=object):
    return meta(b"NewComponent", (base,), {})


class Source(with_metaclass(ComponentMetaClass)):
    def __init__(self, plumber, params):
        self.plumber = plumber
        self.chain = None
        self.params = attrdict(params or {})

    def start(self):
        raise NotImplementedError("Sources should implement their start method")

    def stop(self):
        raise NotImplementedError("Sources should implement their stop method")

    def __repr__(self):
        return "<{}:{}>".format(self.__class__.__name__, id(self))


class DummySource(Source):
    def start(self):
        pass

    def stop(self):
        pass


class Destination(with_metaclass(ComponentMetaClass)):
    def __init__(self, plumber, params):
        self.plumber = self.plumber
        self.params = attrdict(params or {})

    def process(self, exchange):
        raise NotImplementedError(
            "Subclass of destination needs to implement the process method")

    def __repr__(self):
        return "<{}:{}>".format(self.__class__.__name__, id(self))


class Channel(with_metaclass(ComponentMetaClass)):
    def __init__(self, plumber, params):
        self.next = None
        self.params = attrdict(params or {})

        if isinstance(params.get('wiretap', None), Destination):
            self.wiretap = params['wiretap'][0](self.plumber, params['wiretap'][1])
        else:
            self.wiretap = None

    def process(self, exchange):
        try:
            if self.wiretap:
                self.wiretap.process(exchange.copy())
            self.next.process(exchange)
        except AttributeError, e:
            pass

    def __repr__(self):
        return "<{}:{}>".format(self.__class__.__name__, id(self))


class Exchange(with_metaclass(ComponentMetaClass)):
    def __init__(self):
        self.id = uuid.uuid4().get_hex()
        self.in_msg = None
        self.out_msg = None
        self.properties = attrdict()

    def copy(self):
        clone = self.__class__()
        clone.in_msg = self.in_msg
        clone.out_msg = self.out_msg
        clone.properties = self.properties.copy()
        return clone

    def __repr__(self):
        return "<{}: ({}, {}, {}, {})>".format(
            self.__class__.__name__,
            self.id, self.properties, self.in_msg, self.out_msg
        )

    def __unicode__(self):
        return "ID: {}\nProperties: {}\nIn Message:\n{}\nOut Message:\n{}".format(
            self.id,
            ", ".join(["{}:{}".format(k,v) for k,v in self.properties]),
            self.in_msg,
            self.out_msg
        )


class Message(with_metaclass(ComponentMetaClass)):
    def __init__(self):
        self.headers = attrdict()
        self.body = None

    def __repr__(self):
        return "<{}: ({}, {})>".format(
            self.__class__.__name__, self.headers, self.body
        )

    def __unicode__(self):
        return "\tHeaders: {}\n\tBody: {}".format(self.headers, self.body)


class Processor(with_metaclass(ComponentMetaClass)):
    def __init__(self, obj):
        self.object = obj
        self.next = None

    def process(self, exchange):
        try:
            self._process(exchange)
        except AttributeError, e:
            raise e

    def _process(self, exchange):
        self.object.process(exchange)
        if self.next:
            self.next.process(exchange)

    def __repr__(self):
        return "<{}:{}>".format(self.__class__.__name__, id(self))
