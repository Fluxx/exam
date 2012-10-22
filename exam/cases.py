import inspect

from decorators import before, after, around


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

    def attrs_of_type(self, kind):
        for base in inspect.getmro(type(self)):
            for value in vars(base).values():
                if type(value) is kind:
                    yield value

    def setUp(self):
        for value in self.attrs_of_type(before):
            value(self)

    def tearDown(self):
        for value in self.attrs_of_type(after):
            value(self)

    def run(self, *args, **kwargs):
        generators = (value(self) for value in self.attrs_of_type(around))
        with MultipleGeneratorsContextManager(*generators):
            super(Exam, self).run(*args, **kwargs)
