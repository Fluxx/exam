from functools import partial
from operator import eq, ne


IRRELEVANT = object()


class ChangeWatcher(object):

    POSTCONDITION_FAILURE_MESSAGE = {
        ne: 'Value did not change',
        eq: 'Value changed from {before} to {after}',
        'invalid': 'Expected after to be {expected_after}, but was {after}'
    }

    def __init__(self, compare, thing, *args, **kwargs):
        self.thing = thing
        self.compare = compare

        self.args = args
        self.kwargs = kwargs

        self.expected_before = kwargs.pop('before', IRRELEVANT)
        self.expected_after = kwargs.pop('after', IRRELEVANT)

    def __enter__(self):
        self.before = self.__apply()

        if not self.expected_before is IRRELEVANT:
            check = self.compare(self.before, self.expected_before)
            assert not check, "Before value expected to be %s, but was %s" % (
                self.expected_before,
                self.before
            )

    def __exit__(self, exec_type, exec_value, traceback):
        if exec_type is not None:
            return False  # reraises original exception

        self.after = self.__apply()

        met_precondition = self.compare(self.before, self.after)
        after_value_matches = self.after == self.expected_after

        # Changed when it wasn't supposed to, or, didn't change when it was
        if not met_precondition:
            self.__raise_postcondition_error(self.compare)
        # Do care about the after value, but it wasn't equal
        elif self.expected_after is not IRRELEVANT and not after_value_matches:
            self.__raise_postcondition_error('invalid')

    def __apply(self):
        return self.thing(*self.args, **self.kwargs)

    def __raise_postcondition_error(self, key):
        message = self.POSTCONDITION_FAILURE_MESSAGE[key]
        raise AssertionError(message.format(**vars(self)))


class AssertsMixin(object):
    assertChanges = partial(ChangeWatcher, ne)
    assertDoesNotChange = partial(
        ChangeWatcher,
        eq,
        before=IRRELEVANT,
        after=IRRELEVANT
    )
