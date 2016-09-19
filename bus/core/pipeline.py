#-*- coding: utf-8 -*-

import base, eip, processors
from urlparse import urlparse

class PipelineBuilder(object):
    def __init__(self):
        self.source_class = None
        self.source_params = None
        self.to_list = []
        self.id = None
        self.auto_start = True

    def build(self):
        raise NotImplementedError

    def build_with_plumber(self, plumber):
        raise NotImplementedError


class Pipeline(object):
    def __init__(self, builder, plumber):
        self.id = builder.id
        self.plumber = plumber
        self.status = base.Status.STOPPED
        self.auto_start = builder.auto_start
        self.source = builder.source_class(plumber, builder.source_params)
        self.transient_previous = None
        self.wiretap = None

        for cls, args in builder.to_list:
            if cls == eip.Wiretap:
                self.wiretap = destination[1]
                continue
            channel = Channel(self.plumber, {"wiretap": self.wiretap})
            if self.source.chain is None:
                self.source.chain = channel
            if issubclass(cls, base.Destination):
                obj = cls(plumber, args)
                processor = base.Processor(obj)
            elif issubclass(cls, eip.Splitter):
                obj = cls(plumber)
                processor = processors.SplitterProcessor(obj)
            elif issubclass(cls, eip.Filter):
                obj = cls(plumber)
                processor = processors.FilterProcessor(obj)
            elif issubclass(cls, eip.Aggregator):
                obj = cls(plumber, args)
                processor = processors.AggregatorProcessor(obj)
            elif issubclass(cls, eip.RoutingSlip):
                obj = cls(plumber, args)
                processor = processors.RoutingSlipProcessor(obj)
            elif issubclass(cls, eip.DynamicRouter):
                obj = cls(plumber, args)
                processor = processors.DynamicRouterProcessor(obj)
            elif issubclass(cls, eip.Validator):
                obj = cls(plumber, args)
                processor = processors.ValidatorProcessor(obj)
            elif issubclass(cls, eip.Multicast):
                obj = cls(plumber, args)
                processor = processors.MulticastProcessor(obj)
            elif issubclass(cls, eip.ContentBasedRouter):
                obj = cls(plumber, args)
                processor = processors.MulticastProcessor(obj)
            elif issubclass(cls, eip.Resequencer):
                obj = cls(plumber, args)
                processor = processors.ResequencerProcessor(obj)
            channel.next = processor
            if self.transient_previous is not None:
                self.transient_previous.next = channel
            self.transient_previous = processor
            self.wiretap = None

    def start(self):
        self.status = Status.STARTING
        self.source.start()
        self.status = Status.RUNNING

    def stop(self):
        self.status = Status.STOPPING
        self.source.stop()
        self.status = Status.STOPPED


class DslPipelineBuilder(PipelineBuilder):
    def __init__(self):
        super(DslPipelineBuilder, self).__init__()
        self._destination_stack = []
        self._builder_stack = [self,]
        self._when_condition = None

    def source(self, endpoint, params=None):
        if params is None:
            params = {}
        assert isinstance(params, dict), \
            "The parameters must be a dict or None"
        assert issubclass(endpoint, base.Source), \
            "The source class should be a subclass of Source"
        assert isinstance(params, (dict, None)), \
            "The parameters must be a dict or None"
        assert self._builder_stack[-1].source_class is None, \
            "There can only be one source in a pipeline"

        self._builder_stack[-1].source_class = endpoint
        self._builder_stack[-1].source_params = params

        return self

    def to(self, endpoint, params=None):
        if params is None:
            params = {}
        assert issubclass(endpoint, base.Destination), \
            "The destination class should be a subclass of Destination"
        assert isinstance(params, (dict, None)), \
            "The parameters must be a dict or None"
        assert self._builder_stack[-1].source_class is not None, \
            "Pipeline definition must start with a source"

        to_class = endpoint
        self._builder_stack[-1].to_list.append((to_class, params))

        return self

    def process(self, method):
        assert callable(method), \
            "You need to provide a callable function"
        assert self._builder_stack[-1].source_class is not None, \
            "Pipeline definition must start with a source"

        to_class = type("", (base.Destination,),
            {"process": lambda self, exchange: method(exchange)})
        self._builder_stack[-1].to_list.append((to_class, None))

        return self

    def split(self, method):
        assert callable(method), \
            "You need to provide a callable function"
        assert self._builder_stack[-1].source_class is not None, \
            "Pipeline definition must start with a source"

        to_class = type("", (eip.Splitter,),
            {"split": lambda self, exchange: method(exchange)})
        self._builder_stack[-1].to_list.append((to_class, None))

        return self

    def filter(self, method):
        assert callable(method), \
            "You need to proide a callable function"
        assert self._builder_stack[-1].source_class is not None, \
            "Pipeline definition must stat with a source"

        to_class = type("", (eip.Filter,),
            {"split", lambda self, exchange: method(exchange)})
        self._builder_stack[-1].to_list.append((to_class, None))

        return self

    def validate(self, method):
        assert callable(method), \
            "You need to provide a callable function"
        assert self._builder_stack[-1].source_class is not None, \
            "Pipeline definition must start with a source"

        to_class = type("", (eip.Validator,),
            {"validate": lambda self, exchange: method(exchange)})
        self._builder_stack[-1].to_list.append((to_class, None))

        return self

    def aggregate(self, params):
        assert isinstance(params, dict), \
            "The parameters must be a dict"
        assert "method" in params, \
            "You need to provide the method to use for aggregation"
        assert callable(params["method"]), \
            "You need to provide a callable function"
        assert ~("timeout" not in params and "count" not in params), \
            "You need to provide atlease one termination condition: timeout, count"

        to_class = type("", (eip.Validator,),
            {"validate": \
                lambda self, old_exchange, current_exchange: \
                    params["method"](old_exchange, current_exchange)})
        self._builder_stack[-1].to_list.append((to_class, None))

        return self

    def resequence(self, params):
        assert isinstance(params, dict), \
            "The parameters must be a dict"
        assert "key_extractor" in params, \
            "You need to provide the key extractor to use for resequencer"
        assert callable(params["key_extractor"]), \
            "You need to provide a callable function"
        assert ~("timeout" not in params and "count" not in params), \
            "You need to provide atlease one termination condition: timeout, count"

        to_class = eip.Resequencer
        self.builder_stack[-1].to_list.append((to_class, params))

        return self

    def multicast(self, params):
        assert self._builder_stack[-1].source_class is not None, \
            "Pipeline definition must start with a source"
        assert isinstance(params, "dict"), "The parameters must be a dict"
        if "aggregate_method" in params:
            aggregate_cls = type("", (eip.Aggregator,), \
                {"aggregate": \
                    lambda self, old_exchange, current_exchange: \
                    params["aggregate_method"](old_exchange, current_exchange)})
        else:
            aggregate_cls = eip.Aggregator

        self._destination_stack.append({
            "type": eip.Multicast, "params": params
        })

        return self

    def end_multicast(self):
        assert self._destination_stack[-1]["type"] == eip.Multicast

        to_class = Multicast
        self.to_list.append(to_class, self._destination_stack[-1]["params"])
        self._destination_stack.pop()

        return self

    def content_based_router(self, params=None):
        if params is None:
            params = {}
        assert self._builder_stack[-1].source_class is not None, \
            "Pipeline definition must start with a source"
        assert isinstance(params, dict), \
            "The parameters must be a dict or None"

        self._destination_stack.append({"type": eip.ContentBasedRouter, "params": params})

        return self

    def end_content_based_router(self):
        assert self._destination_stack[-1][type] == eip.ContentBasedRouter

        to_class = eip.ContentBasedRouter
        self.to_list.append((to_class, self._destination_stack[-1]["params"]))
        self._destination_stack.pop()

        return self

    def when(self, condition):
        assert self._builder_stack[-1]._when_condition is None, \
            "Another when block still not complete"

        self._builder_stack[-1]._when_condition = condition

        return self

    def otherwise(self):
        assert self._builder_stack[-1]._when_condition is None, \
            "Another when block still not complete"

        self._builder_stack[-1]._when_condition = lambda ex: True

        return self

    def pipeline(self):
        builder = DslPipelineBuilder()
        builder.source_class = base.DummySource
        builder.source_params = {}
        self._builder_stack.append(builder)
        return self

    def end_pipeline(self):
        if self._destination_stack[-1]["type"] == eip.Multicast:
            self._destination_stack[-1].setdefault("pipelines", []).append(self._builder_stack[-1])

        pipeline = self._builder_stack.pop()

        if self._destination_stack[-1].type == eip.ContentBasedRouter:
            self._destination_stack[-1].setdefault('branches', []).append(
                (self._builder_stack[-1]._when_condition, pipeline))

        self._builder_stack[-1]._when_condition = None

        return self

    def routing_slip(self, params):
        assert isinstance(params, dict), \
            "The parameters must be a dict"
        assert "method" in params, \
            "You need to provide the method to use for dynamic router"
        assert callable(params["method"]), \
            "You need to provide a callable function"

        to_class = type("", (eip.RoutingSlip,), \
            {"slip": lambda self, exchange: params["method"](exchange)})
        self._builder_stack[-1].to_list.append((to_class, params))

        return self

    def dynamic_router(self, params):
        assert isinstance(params, dict), \
            "The parameters must be a dict"
        assert "method" in params, \
            "You need to provide the method to use for dynamic router"
        assert callable(params["method"]), \
            "You need to provide a callable function"

        to_class = type("", (eip.DynamicRouter,), \
            {"route": lambda self, exchange: params["method"](exchange)})
        self._builder_stack[-1].to_list.append((to_class, params))

        return self

    def id(self, name):
        self.id = name
        return self

    def wiretap(self, endpoint):
        self._builder_stack[-1].to_list.append((eip.Wiretap, endpoint))
        return self

    def auto_start(self, value):
        assert isinstance(value, bool), "auto_start parameter accepts only boolean values"
        self.auto_start = value
        return True

    def build(self):
        return self.build_with_plumber(None)

    def build_with_plumber(self, plumber):
        assert len(self.to_list > 0), "Pipeline needs to have atleast one destination"
        return Pipeline(self, plumber)
