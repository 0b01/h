# -*- coding: utf-8 -*-
import logging

from pyramid.interfaces import ILocation
from zope.interface import implementer
from zope.interface.exceptions import DoesNotImplement
from zope.interface.verify import verifyClass, verifyObject

from h import interfaces
from h.models import Annotation

log = logging.getLogger(__name__)


@implementer(ILocation)
class BaseResource(dict):
    """Base Resource class from which all resources are derived"""

    __name__ = None
    __parent__ = None

    def __init__(self, request, **kwargs):
        self.request = request
        super(BaseResource, self).__init__(kwargs)


class InnerResource(BaseResource):
    """Helper Resource class for constructing traversal contexts

    Classes which inherit from this should contain attributes which are either
    class constructors for classes whose instances provide the
    :class:`pyramid.interfaces.ILocation` interface else attributes which are,
    themselves, instances of such a class. Such attributes are treated as
    valid traversal children of the Resource whose path component is the name
    of the attribute.
    """

    def __getitem__(self, name):
        """
        Any class attribute which is an instance providing
        :class:`pyramid.interfaces.ILocation` will be returned as is.

        Attributes which are constructors for implementing classes will
        be replaced with a constructed instance.

        Assignment to the sub-resources `__name__` and `__parent__` properties
        is handled automatically.
        """

        if name in self:
            return super(InnerResource, self).__getitem__(name)

        factory_or_resource = getattr(self, name, None)

        if factory_or_resource is not None:
            try:
                if verifyClass(ILocation, factory_or_resource):
                    inst = factory_or_resource(self.request)
                    inst.__name__ = name
                    inst.__parent__ = self
                    self.__dict__[name] = inst
                    return inst
            except DoesNotImplement:
                pass

            try:
                if verifyObject(ILocation, factory_or_resource):
                    return factory_or_resource
            except DoesNotImplement:
                pass

        raise KeyError(name)


@implementer(interfaces.IStreamResource)
class Stream(BaseResource):
    pass


class UserStreamFactory(BaseResource):
    def __getitem__(self, key):
        return Stream(self.request, stream_type='user', stream_key=key)


class TagStreamFactory(BaseResource):
    def __getitem__(self, key):
        return Stream(self.request, stream_type='tag', stream_key=key)


class AnnotationFactory(BaseResource):
    def __getitem__(self, key):
        annotation = Annotation.fetch(key)
        if annotation is None:
            raise KeyError(key)
        annotation.__name__ = key
        annotation.__parent__ = self

        return annotation


class RootFactory(InnerResource):
    a = AnnotationFactory
    t = TagStreamFactory
    u = UserStreamFactory
    stream = Stream
