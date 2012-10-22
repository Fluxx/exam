from decorators import before, after


class Examify(type):

    DECORATORS = dict(setUp=before, tearDown=after)

    def __new__(cls, name, bases, attrs):
        values = attrs.values()

        for base in bases:
            values.extend(vars(base).values())

        for method, kind in cls.DECORATORS.items():
            key = '%s_methods' % method
            attrs.setdefault(key, [])
            [attrs[key].append(v) for v in values if type(v) is kind]

        return super(Examify, cls).__new__(cls, name, bases, attrs)


class Exam(object):

    __metaclass__ = Examify

    setUp = lambda self: [method(self) for method in self.setUp_methods]
    tearDown = lambda self: [method(self) for method in self.tearDown_methods]
