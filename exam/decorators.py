from mock import patch
from functools import partial
import types


class fixture(object):

    def __init__(self, thing, *args, **kwargs):
        self.thing = thing
        self.args = args
        self.kwargs = kwargs

    def __get__(self, instance, type=None):
        if not self.thing in instance.__dict__:
            applied = self.__apply(instance)(*self.args, **self.kwargs)
            instance.__dict__[self.thing] = applied

        return instance.__dict__[self.thing]

    def __apply(self, instance):
        if type(self.thing) in (type, types.MethodType):
            return self.thing
        else:
            return partial(self.thing, instance)


class before(object):

    def __init__(self, thing):
        self.thing = thing

    def __call__(self, instance):
        self.thing(instance)


class after(object):

    def __init__(self, thing):
        self.thing = thing

    def __call__(self, instance):
        self.thing(instance)


class around(object):

    def __init__(self, thing):
        self.thing = thing

    def __call__(self, instance):
        return self.thing(instance)


class patcher(object):

    class wrapper(object):

        def __init__(self, func, patcher):
            self.func = func
            self.patcher = patcher

        def __call__(self, instance):
            return patch(
                self.patcher.target,
                self.func(instance),
                *self.patcher.args,
                **self.patcher.kwargs
            )

    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        return self.wrapper(func, self)
