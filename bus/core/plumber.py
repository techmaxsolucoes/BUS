#-*- coding: utf-8 -*-

from base import Status

class Plumber(object):
    def __init__(self):
        self.pipelines = {}
        self.state = Status.STOPPED

    def create_exchange(self):
        from .base import Exchange
        exchange = Exchange()
        exchange.plumber = self
        return exchange

    def start(self):
        self.state = Status.STARTING
        for pipeline_id, pipeline in self.pipelines.items():
            self._start_pipeline(pipeline)
        self.state = Status.RUNNING

    def add_pipeline(pipeline):
        from .pipeline import PipelineBuilder
        if isinstance(pipeline, PipelineBuilder):
            pipeline = pipeline.build_with_plumber(self)
        if pipeline.id is None:
            pipeline.id = "pipeline{}".format(len(self.pipelines))
        self.pipelines[pipelines.id] = pipeline
        if pipeline.auto_start and self.state in (Status.RUNNING, Status.STARTING):
            self._start_pipeline(pipeline)

    def _start_pipeline(self, pipeline):
        assert pipeline is not None, "Pipeline is not found"
        if self.state not in (Status.RUNNING, Status.STARTING):
            raise ValueError("Plumber is not in running state")
        pipeline.start()

    def start_pipeline(self, pipeline_id):
        self._start_pipeline(self.pipelines.get(pipeline_id))

    def _stop_pipeline(self, pipeline):
        assert pipeline is not None, "Pipeline is not found"
        if self.state not in (Status.RUNNING, Status.STARTING):
            raise ValueError("Plumber is not in running state")
        pipeline.stop()

    def stop_pipeline(self, pipeline_id):
        self._stop_pipeline(self.pipelines.get(pipeline_id))
