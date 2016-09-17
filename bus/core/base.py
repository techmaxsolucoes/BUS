#-*- coding: utf-8 -*-

from __future__ import unicode_literals
import uuid


class Status:
    STARTING = 1
    STOPPING = 2
    RUNNING = 3
    STOPPED = 4


class Source(object):
    def __init__(self, plumber, params):
        self.plumber = plumber
        self.chain = None
        self.params = params

    def start(self):
        raise NotImplementedError("Sources should implement their start method")

    def stop(self):
        raise NotImplementedError("Sources should implement their stop method")

    def __repr__(self):
        return "<{}:{}>".format(self.__class__.__name__, id(self))


class DummySource(object):
    def start(self):
        pass

    def stop(self):
        pass


class Destination(object):
    def __init__(self, plumber, params):
        self.plumber = self.plumber
        self.params = self.params

    def process(self, exchange):
        raise NotImplementedError(
            "Subclass of destination needs to implement the process method")

    def __repr__(self):
        return "<{}:{}>".format(self.__class__.__name__, id(self))


class Channel(object):
    def __init__(self, plumber, params):
        self.next = None
        self.params = self.params

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


class Exchange(object):
    def __init__(self):
        self.id = uuid.uuid4().get_hex()
        self.in_msg = None
        self.out_msg = None
        self.properties = {}

    def copy(self):
        clone = self.__class__()
        clone.in_msg = self.in_msg
        clone.out_msg = self.out_msg
        clone.properties self.properties.copy()
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


class Message(object):
    def __init__(self):
        self.headers = {}
        self.body = {}

    def __repr__(self):
        return "<{}: ({}, {})>".format(
            self.__class__.__name__, self.headers, self.body
        )

    def __unicode__(self):
        return "\tHeaders: {}\n\tBody: {}".format(self.headers, self.body)


class Processor(object):
    def __init__(self, obj):
        self.object = obj
        self.next = None

    def process(self, exchange):
        try:
            self._process(exchange):
        except AttributeError, e:
            raise e

    def _process(self, exchange):
        self.object.process(exchange)
        if self.next:
            self.next.process(exchange)

    def __repr__(self):
        return "<{}:{}>".format(self.__class__.__name__, id(self))
