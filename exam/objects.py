from __future__ import absolute_import


def always(value):
    return lambda *a, **k: value

noop = no_op = always(None)


class call(tuple):
    """
    Stores args and kwargs it was constructed with, and compares equal to other
    call objects that were called with the same (using equality, ==) arguments.

    >>> from exam.objects import call
    >>> call(1, 2, b=[3]) == call(1, 2, b=[3])
    True
    """

    def __new__(cls, *args, **kwargs):
        arguments = (args, tuple(sorted(kwargs.items())))
        return tuple.__new__(cls, arguments)


class effect(list):
    """
    Helper class that is itself callable, whose return values when called are
    configured via the tuples passed in to the constructor. Useful to build
    ``side_effect`` callables for Mock objects.  Raises TypeError if called with
    arguments that it was not configured with:

    >>> from exam.objects import call, effect
    >>> side_effect = effect((call(1), 'with 1'), (call(2), 'with 2'))
    >>> side_effect(1)
    'with 1'
    >>> side_effect(2)
    'with 2'

    Call argument equality is checked via equality (==) of the ``call``` object,
    which is the 0th item of the configuration tuple passed in to the ``effect``
    constructor.  By default, ``call`` objects are just themselves ``tuple``s,
    and will use their default equality checking.

    If you would like to customize this behavior, subclass `effect` and redefine
    your own `call_class` class variable.  I.e.

        class myeffect(effect):
            call_class = my_call_class
    """

    call_class = call

    def __init__(self, *calls):
        """
        :param calls: Two-item tuple containing call and the return value.
        :type calls: :class:`efffect.call_class`
        """
        super(effect, self).__init__(calls)

    def __call__(self, *args, **kwargs):
        this_call = self.call_class(*args, **kwargs)

        for call_obj, return_value in self:
            if call_obj == this_call:
                return return_value

        raise TypeError('Unknown effect for: %s, %s' % (args, kwargs))
