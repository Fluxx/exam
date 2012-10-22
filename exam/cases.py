import inspect

from decorators import before, after


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
