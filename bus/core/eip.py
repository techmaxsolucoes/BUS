#-*- coding: utf-8 -*-

from __future__ import unicode_literals

from base import ComponentMetaClass, with_metaclass

class Aggregator(with_metaclass(ComponentMetaClass)):
    def __init__(self, plumber, params):
        self.plumber = plumber
        self.timeout = params.get("timeout")
        self.count = params.get("count")

    def aggregate(self, old_exchange, current_exchange):
        return current_exchange


class ContentBasedRouter(with_metaclass(ComponentMetaClass)):
    def __init__(self, plumber, params):
        self.plumber = plumber
        self.branches = []

        for condition, builder in params:
            self.branches.append((condition, builder.build_with_plumber(plumber)))

    def get_valid_pipeline(self, exchange):
        for condition, pipeline in self.branches:
            if condition(exchange):
                return pipeline
        return None

class DynamicRouter(with_metaclass(ComponentMetaClass)):
    def __init__(plumber, params):
        self.plumber = plumber
        self.params = params

    def route(self, exchange):
        raise NotImplementedError("Subclass must implement the route method")


class Filter(with_metaclass(ComponentMetaClass)):
    def __init__(plumber):
        self.plumber = plumber

    def filter(self, exchange):
        raise NotImplementedError("Derived classes should implement the filter method")


class Multicast(with_metaclass(ComponentMetaClass)):
    def __init__(plumber, params):
        self.plumber = plumber
        self.params = params
        self.aggregator = params.get("aggregator")(plumber, {})
        self.pipelines = []
        for builder in params.get("pipelines", []):
            self.pipelines.append(builder.build_with_plumber(plumber))

class Resequencer(with_metaclass(ComponentMetaClass)):
    def __init__(self, plumber, params):
        self.plumber = plumber
        self.timeout = params.get("timeout")
        self.count = params.get("count")
        self.key_extractor = params.get("key_extractor")
        self.reverse = params.get("reverse", False)

    def resequence(self, exchange):
        exchange.sort(key=self.key_extractor, reverse=self.reverse)


class RoutingSlip(with_metaclass(ComponentMetaClass)):
    def __init__(self, plumber, params):
        self.plumber = plumber
        self.params = params

    def slip(self, exchange):
        raise NotImplementedError("Subclass must implement slip method")


class Splitter(with_metaclass(ComponentMetaClass)):
    def __init__(self, plumber, params):
        self.plumber = plumber

    def split(self, exchange):
        raise NotImplementedError("Subclass must implement split method")


class Validator(with_metaclass(ComponentMetaClass)):
    def __init__(self, plumber):
        self.plumber = plumber

    def validate(self, exchange):
        raise NotImplementedError("Derived classes should implement the validate method")


class Wiretap(with_metaclass(ComponentMetaClass)):
    def __init__(self, endpoint):
        self.endpoint = endpoint
