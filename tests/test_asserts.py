from unittest2 import TestCase

from exam import Exam, fixture
from exam.asserts import AssertsMixin

from describe import expect


class AssertChangesMixin(Exam, TestCase):

    case = fixture(AssertsMixin)
    thing = fixture(list)

    def no_op_context(self, *args, **kwargs):
        with self.case.assertChanges(len, self.thing, *args, **kwargs):
            pass

    def test_checks_change_on_callable_passed(self):
        with self.case.assertChanges(len, self.thing, before=0, after=1):
            self.thing.append(1)

    def test_after_check_asserts_ends_on_after_value(self):
        self.thing.append(1)
        with self.case.assertChanges(len, self.thing, after=2):
            self.thing.append(1)

    def test_before_check_asserts_starts_on_before_value(self):
        self.thing.append(1)
        with self.case.assertChanges(len, self.thing, before=1):
            self.thing.append(1)
            self.thing.append(2)

    def test_verifies_value_must_change_no_matter_what(self):
        self.thing.append(1)

        with expect.to_raise_error(AssertionError):
            self.no_op_context(after=1)

        with expect.to_raise_error(AssertionError):
            self.no_op_context(before=1)

        with expect.to_raise_error(AssertionError):
            self.no_op_context()

    def test_reraises_exception_if_raised_in_context(self):
        with self.assertRaises(NameError):
            with self.case.assertChanges(len, self.thing, after=5):
                self.thing.append(1)
                undefined_name
