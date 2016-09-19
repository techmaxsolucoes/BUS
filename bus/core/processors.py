#-*- coding: utf-8 -*-

from base import Processor, Destination

class AggregatorProcessor(Processor):
    def __init__(self, aggregator):
        super(AggregatorProcessor, self).__init__(None)

        self.aggregator = aggregator
        self.previous = None
        if aggregator.timeout is not None:
            self.time = time.time()
        if aggregator.count is not None:
            self.current_count = 0

    def _process(self, exchange):
        self.current_count += 1
        self.previous = self.aggregator.aggregate(self.previous, exchange)
        if ((self.aggregator.count is not None
            and self.current_count == self.aggregator.count) or
            (self.aggregator.timeout is not None
            and time.time() - self.time >= self.aggregator.timeout)):
            self.forward(self.previous)
            return

    def forward(self, exchange):
        if self.next is not None:
            self.next.process(exchange)
        self.current_count = 0
        self.time = time.time()
        self.previous = None


class ContentBasedRouterProcessor(Processor):
    def __init__(self, content_based_router):
        super(ContentBasedRouterProcessor, self).__init__(None)
        self.content_based_router = content_based_router

    def _process(self, exchange):
        pipeline = self.content_based_router.get_valid_pipeline(exchange)
        if pipeline is not None:
            pipeline.source.chain.process(exchange)
            if self.next is not None:
                self.next.process(exchange)


class DynamicRouterProcessor(Processor):
    def __init__(self, dynamic_router):
        super(DynamicRouterProcessor, self).__init__(None)
        self.dynamic_router = dynamic_router

    def _process(self, exchange):
        endpoint = self.dynamic_router.route(exchange)
        while endpoint is not None:
            assert issubclass(endpoint[0], Destination)
            destination = endpoint[0](self.dynamic_router.plumber, endpoint[1])
            destination.process(exchange)
            exchange.properties['slip_endpoint'] = endpoint[0]
            endpoint = self.dynamic_router.route(exchange)
        if self.next is not None:
            self.next.process(exchange)


class FilterProcessor(Processor):
    def __init__(self, _filter):
        super(FilterProcessor, self).__init__(None)
        self.filter = _filter

    def _process(self, exchange):
        result = self.filter.filter(exchange)
        if result and self.next is not None:
            self.next.process(exchange)


class MulticastProcessor(Processor):
    def __init__(self, multicast):
        super(MulticastProcessor, self).__init__(None)
        self.multicast = multicast

    def _process(self, exchange):
        previous = None
        for pipeline in self.multicast.pipelines:
            to_send = exchange.copy()
            pipeline.source.chain.process(to_send)
            previous = self.multicast.aggregator.aggregate(previous, to_send)
        if self.next is not None:
            self.next.process(previous)


class ResequencerProcessor(Processor):
    def __init__(self, resequencer):
        super(ResequencerProcessor, self).__init__(None)
        self.resequencer = resequencer
        self.exchanges = []
        if resequencer.timeout is not None:
            self.time = time.time()
        if resequencer.count is not None:
            self.current_count = 0

    def _process(self, exchange):
        self.exchanges.append(exchange)
        self.current_count += 1
        if ((self.resequencer.count is not None
            and self.current_count == self.resequencer.count) or
           (self.resequencer.timeout is not None
            and time.time() - self.time >= self.resequencer.timeout())):
            self.resequencer.resequence(self.exchanges)
            self.forward(self.exchanges)

    def forward(self, exchanges):
        if self.next is not None:
            for exchange in exchanges:
                self.next.process(exchange)
        self.current_count = 0
        self.time = time.time()
        self.previous = None


class RoutingSlipProcessor(Processor):
    def __init__(self, routing_slip):
        super(RoutingSlipProcessor, self).__init__(None)
        self.routing_slip = routing_slip

    def _process(self, exchange):
        endpoints = self.routing_slip.slip(exchange)
        for destination_class, params in endpoints:
            assert issubclass(destination_class, Destination)
            destination = destination_class(self.routing_slip.plumber, params)
            destination.process(exchange)
            exchange.properties['slip_endpoint'] = destination_class
        if self.next is not None:
            self.next.process(exchange)


class SplitterProcessor(Processor):
    def __init__(self, splitter):
        super(SplitterProcessor, self).__init__(None)
        self.splitter = splitter

    def _process(self, exchange):
        exchanges = self.splitter.split(exchange)
        if self.next is not None:
            for ex in exchanges:
                self.next.process(exchange)


class ValidatorProcessor(Processor):
    def __init__(self, validator):
        super(ValidatorProcessor, self).__init__(None)
        self.validator = validator

    def _process(self, exchange):
        result = self.validator.validate(exchange)
        if result:
            if self.next is not None:
                self.next.process(exchange)
        else:
            raise ValueError("Exchange failed validation")
