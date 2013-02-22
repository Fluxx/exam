from __future__ import absolute_import

from exam.decorators import before, after, around, patcher  # NOQA
from exam.objects import noop  # NOQA
from exam.asserts import AssertsMixin

import inspect


def unique(iterable):
    seen = set()
    for value in iterable:
        if value not in seen:
            seen.add(value)
            yield value


class MultipleGeneratorsContextManager(object):

    def __init__(self, *generators):
        self.generators = generators

    def __enter__(self, *args, **kwargs):
        [g.next() for g in self.generators]

    def __exit__(self, *args, **kwargs):
        for generator in reversed(self.generators):
            try:
                generator.next()
            except StopIteration:
                pass


class Exam(AssertsMixin):

    @before
    def setup_patchers(self):
        for attr, patchr in self.attrs_of_type(patcher):
            patch_object = patchr.build_patch(self)
            setattr(self, attr, patch_object.start())
            self.addCleanup(patch_object.stop)

    def attrs_of_type(self, kind):
        for base in reversed(inspect.getmro(type(self))):
            for attr, class_value in vars(base).iteritems():
                resolved_value = getattr(type(self), attr, False)

                if type(resolved_value) is not kind:
                    continue
                # If the attribute inside of this base is not the exact same
                # value as the one in type(self), that means that it's been
                # overwritten somewhere down the line and we shall skip it
                elif class_value is not resolved_value:
                    continue
                else:
                    yield attr, resolved_value

    def run_before_hooks(self):
        for _, value in self.attrs_of_type(before):
            value(self)

    def run_after_hooks(self):
        for _, value in self.attrs_of_type(after):
            value(self)

    def run(self, *args, **kwargs):
        generators = (value(self) for _, value in self.attrs_of_type(around))
        with MultipleGeneratorsContextManager(*generators):
            self.run_before_hooks()
            getattr(super(Exam, self), 'run', noop)(*args, **kwargs)
            self.run_after_hooks()
