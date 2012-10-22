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
