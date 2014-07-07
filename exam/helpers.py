from __future__ import absolute_import

import shutil
import os
import functools

from mock import MagicMock, patch, call


def rm_f(path):
    try:
        # Assume it's a directory
        shutil.rmtree(path, ignore_errors=True)
    except OSError:
        # Directory delete failed, so it's likely a file
        os.remove(path)


def track(**mocks):
    tracker = MagicMock()

    for name, mocker in mocks.items():
        tracker.attach_mock(mocker, name)

    return tracker


def intercept(obj, methodname, wrapper):
    """
    Wraps an existing method on an object with the provided generator, which
    will be "sent" the value when it yields control.

    ::

        >>> def ensure_primary_key_is_set():
        ...     assert model.pk is None
        ...     saved = yield
        ...     aasert model is saved
        ...     assert model.pk is not None
        ...
        >>> intercept(model, 'save', ensure_primary_key_is_set)
        >>> model.save()

    :param obj: the object that has the method to be wrapped
    :type obj: :class:`object`
    :param methodname: the name of the method that will be wrapped
    :type methodname: :class:`str`
    :param wrapper: the wrapper
    :type wrapper: generator callable
    """
    original = getattr(obj, methodname)

    def replacement(*args, **kwargs):
        wrapfn = wrapper(*args, **kwargs)
        wrapfn.send(None)
        result = original(*args, **kwargs)
        try:
            wrapfn.send(result)
        except StopIteration:
            return result
        else:
            raise AssertionError('Generator did not stop')

    def unwrap():
        """
        Restores the method to it's original (unwrapped) state.
        """
        setattr(obj, methodname, original)

    replacement.unwrap = unwrap

    setattr(obj, methodname, replacement)


class mock_import(patch.dict):

    FROM_X_GET_Y = lambda s, x, y: getattr(x, y)

    def __init__(self, path):
        self.mock = MagicMock()
        self.path = path
        self.modules = {self.base: self.mock}

        for i in range(len(self.remainder)):
            tail_parts = self.remainder[0:i + 1]
            key = '.'.join([self.base] + tail_parts)
            reduction = functools.reduce(self.FROM_X_GET_Y,
                                         tail_parts, self.mock)
            self.modules[key] = reduction

        super(mock_import, self).__init__('sys.modules', self.modules)

    @property
    def base(self):
        return self.path.split('.')[0]

    @property
    def remainder(self):
        return self.path.split('.')[1:]

    def __enter__(self):
        super(mock_import, self).__enter__()
        return self.modules[self.path]

    def __call__(self, func):
        super(mock_import, self).__call__(func)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            args = list(args)
            args.insert(1, self.modules[self.path])

            with self:
                func(*args, **kwargs)

        return inner


class effect(list):
    """
    Helper class that is itself callable, whose return values when called are
    configured via the tuples passed in to the constructor. Useful to build
    ``side_effect`` callables for Mock objects.  Raises TypeError if
    called with arguments that it was not configured with:

    >>> from exam.objects import call, effect
    >>> side_effect = effect((call(1), 'with 1'), (call(2), 'with 2'))
    >>> side_effect(1)
    'with 1'
    >>> side_effect(2)
    'with 2'

    Call argument equality is checked via equality (==)
    of the ``call``` object, which is the 0th item of the configuration
    tuple passed in to the ``effect`` constructor.
    By default, ``call`` objects are just ``mock.call`` objects.

    If you would like to customize this behavior,
    subclass `effect` and redefine your own `call_class`
    class variable.  I.e.

        class myeffect(effect):
            call_class = my_call_class
    """

    call_class = call

    def __init__(self, *calls):
        """
        :param calls: Two-item tuple containing call and the return value.
        :type calls: :class:`effect.call_class`
        """
        super(effect, self).__init__(calls)

    def __call__(self, *args, **kwargs):
        this_call = self.call_class(*args, **kwargs)

        for call_obj, return_value in self:
            if call_obj == this_call:
                return return_value

        raise TypeError('Unknown effect for: %r, %r' % (args, kwargs))
