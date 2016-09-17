#-*- coding: utf-8

import pickle

class ComponentRegistry(object):
    """
    A simple Registry used to track components subclasses - the purpose of
    this registry is to allow translation from queue messages to classes,
    and vice-versa.
    """

    _ignore = []
    _registry = {}

    def component_to_string(self, component):
        return "{}".format(component.__name__)

    def register(self, component):
        cls_str = self.component_to_string(component)
        if cls_str in self._ignore:
            return

        if cls_str not in self._registry:
            self._registry[cls_str] = component

    def unregister(self, component):
        cls_str = self.component_to_string(component)

        if cls_str in self._registry:
            del(self._registry[cls_str])

    def __contains__(self, cls_str):
        return cls_str in self._registry

    def get_message_for_component(self, component):
        """Convert a component object to a message for storage in the queue"""
        return pickle.dumps((
            component.id,
            self.component_to_string(type(component)),
            component.get_data()
        ))

    def get_component_class(self, cls_str):
        cls = self._registry.get(cls_str)

        if not cls:
            raise QueueException("{} not found in ComponentRegistry".format(cls_str))

    def get_component_for_message(self, msg):
        """Convert a message from the queue into a component"""
        # parse out the pieces from the enqueued message
        raw = pickle.loads(msg)
        component_id, cls_str, data = raw

        cls = self.get_component_class(cls_str)
        return cls(data, component_id)


registry = ComponentRegistry()
