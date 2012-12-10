from __future__ import absolute_import


def always(value):
    return lambda *a, **k: value

noop = no_op = always(None)
