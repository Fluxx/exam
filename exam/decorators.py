from __future__ import absolute_import

from mock import patch
from functools import partial, wraps
import types

import exam.cases


class fixture(object):

    def __init__(self, thing, *args, **kwargs):
        self.thing = thing
        self.args = args
        self.kwargs = kwargs

    def __get__(self, testcase, type=None):
        if not testcase:
            # Test case fixture was accesse as a class property, so just return
            # this fixture itself.
            return self
        elif self not in testcase.__dict__:
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
        # If not, it means that's it's a vanilla function,
        # so either a decorated instance method in the test case
        # body or a lambda.  In either of those
        # cases, it's called with the test case instance (self) to the author.
        else:
            return partial(self.thing, testcase)


class base(object):

    def __init__(self, *things):
        self.init_callables = things

    def __call__(self, instance):
        return self.init_callables[0](instance)


class before(base):

    def __call__(self, thing):
        # There a couple possible situations at this point:
        #
        # If ``thing`` is an instance of a test case, this means that we
        # ``init_callable`` is the function we want to decorate.  As such,
        # simply call that callable with the instance.
        if isinstance(thing, exam.cases.Exam):
            return self.init_callables[0](thing)
        # If ``thing is not an instance of the test case, it means thi before
        # hook was constructed with a callable that we need to run before
        # actually running the decorated function.
        # It also means that ``thing`` is the function we're
        # decorating, so we need to return a callable that
        # accepts a test case instance and, when called, calls the
        # ``init_callable`` first, followed by the actual function we are
        # decorating.
        else:
            @wraps(thing)
            def inner(testcase):
                [f(testcase) for f in self.init_callables]
                thing(testcase)

            return inner


class after(base):
    pass


class around(base):
    pass


class patcher(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.func = None
        self.patch_func = patch

    def __call__(self, func):
        self.func = func
        return self

    def build_patch(self, instance):
        if self.func:
            self.kwargs['new'] = self.func(instance)

        return self.patch_func(*self.args, **self.kwargs)

    @classmethod
    def object(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        instance.patch_func = patch.object
        return instance
