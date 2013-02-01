from __future__ import absolute_import


def always(value):
    return lambda *a, **k: value

noop = no_op = always(None)


class call(tuple):

    def __new__(cls, *args, **kwargs):
        arguments = (args, tuple(sorted(kwargs.items())))
        return tuple.__new__(cls, arguments)


class effect(dict):

    def __call__(self, *args, **kwargs):
        try:
            return self[call(*args, **kwargs)]
        except KeyError:
            raise TypeError('Unknown effect for: %s, %s' % (args, kwargs))
