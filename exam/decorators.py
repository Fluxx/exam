from __future__ import absolute_import

from mock import patch
from functools import partial
import types


class fixture(object):

    def __init__(self, thing, *args, **kwargs):
        self.thing = thing
        self.args = args
        self.kwargs = kwargs

    def __get__(self, testcase, type=None):
        if not self in testcase.__dict__:
            # If this fixture is not present in the test case's __dict__,
            # freshly apply this fixture and store that in the dict, keyed by
            # self
            application = self.__apply(testcase)(*self.args, **self.kwargs)
            testcase.__dict__[self] = application

        return testcase.__dict__[self]

    def __apply(self, testcase):
        # If self.thing is a method type, it means that the function is already
        # bound to a class and therefore we should treat it just like a normal
        # functuion and return it.
        if type(self.thing) in (type, types.MethodType):
            return self.thing
        # If not, it means that's it's a vanilla function, so either a decorated
        # instance method in the test case body or a lambda.  In either of those
        # cases, it's called with the test case instance (self) to the author.
        else:
            return partial(self.thing, testcase)


class base(object):

    def __init__(self, thing):
        self.thing = thing

    def __call__(self, instance):
        return self.thing(instance)


class before(base):
    pass


class after(base):
    pass


class around(base):
    pass


class patcher(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.func = None

    def __call__(self, func):
        self.func = func
        return self

    def build_patch(self, instance):
        if self.func:
            self.kwargs['new'] = self.func(instance)

        return patch(*self.args, **self.kwargs)
