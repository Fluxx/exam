from __future__ import absolute_import

import inspect

from exam.decorators import before, after, around, patcher  # NOQA
from exam.objects import noop  # NOQA


class MultipleGeneratorsContextManager(object):

    def __init__(self, *generators):
        self.generators = generators

    def __enter__(self, *args, **kwargs):
        [g.next() for g in self.generators]

    def __exit__(self, *args, **kwargs):
        for generator in self.generators:
            try:
                generator.next()
            except StopIteration:
                pass


class Exam(object):

    @before
    def setup_patchers(self):
        for attr, patchr in self.attrs_of_type(patcher):
            patch_object = patchr.build_patch(self)
            setattr(self, attr, patch_object.start())
            self.addCleanup(patch_object.stop)

    def attrs_of_type(self, kind):
        for base in inspect.getmro(type(self)):
            for attr, value in vars(base).items():
                if type(value) is kind:
                    yield attr, value

    def setUp(self):
        getattr(super(Exam, self), 'setUp', noop)()

        for _, value in self.attrs_of_type(before):
            value(self)

    def tearDown(self):
        getattr(super(Exam, self), 'tearDown', noop)()

        for _, value in self.attrs_of_type(after):
            value(self)

    def run(self, *args, **kwargs):
        generators = (value(self) for _, value in self.attrs_of_type(around))
        with MultipleGeneratorsContextManager(*generators):
            super(Exam, self).run(*args, **kwargs)
