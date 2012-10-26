from mock import patch


class fixture(object):

    def __init__(self, thing):
        self.thing = thing

    def __get__(self, obj, type=None):
        if not self.thing in obj.__dict__:
            obj.__dict__[self.thing] = self.thing(obj)

        return obj.__dict__[self.thing]


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
