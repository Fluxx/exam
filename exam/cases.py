import inspect

from decorators import before, after, around, patcher


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
    def setup_wrapped_patchers(self):
        for wrapped in self.attrs_of_type(patcher.wrapper):
            ptchr = wrapped(self)
            setattr(self, wrapped.func.__name__, ptchr.start())
            self.addCleanup(ptchr.stop)

    @before
    def setup_patchers(self):
        for ptchr in self.attrs_of_type(patcher):
            # Extract out patcher.wrapper, via a patcher(), then call that
            # wrapper to extract out the actual patch object
            wrapped = ptchr(None)
            patch_object = wrapped(self)
            patch_object.start()
            self.addCleanup(patch_object.stop)

            # And add a handle back to the mock patch object for the local
            # patch object
            ptchr.applied = patch_object

    def attrs_of_type(self, kind):
        for base in inspect.getmro(type(self)):
            for value in vars(base).values():
                if type(value) is kind:
                    yield value

    def setUp(self):
        # Run each before
        for value in self.attrs_of_type(before):
            value(self)

    def tearDown(self):
        for value in self.attrs_of_type(after):
            value(self)

    def run(self, *args, **kwargs):
        generators = (value(self) for value in self.attrs_of_type(around))
        with MultipleGeneratorsContextManager(*generators):
            super(Exam, self).run(*args, **kwargs)
