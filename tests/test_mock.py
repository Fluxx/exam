from unittest2 import TestCase

from exam.mock import Mock
from exam.decorators import fixture, before


class MockTest(TestCase):

    mock = fixture(Mock)

    @before
    def assert_mock_clean(self):
        self.mock.assert_not_called()

    def test_assert_called_asserts_mock_was_called(self):
        self.assertRaises(AssertionError, self.mock.assert_called)

        self.mock()
        self.mock.assert_called()

        self.mock.reset_mock()
        self.assertRaises(AssertionError, self.mock.assert_called)

    def test_assert_not_called_asserts_mock_was_not_called(self):
        self.mock()
        self.assertRaises(AssertionError, self.mock.assert_not_called)

        self.mock.reset_mock()
        self.mock.assert_not_called()

    def test_assert_not_called_with_asserts_not_called_with_args(self):
        self.mock(1, 2, three=4)
        self.mock.assert_called_with(1, 2, three=4)

        self.mock.assert_not_called_with(1, 2, four=5)
        self.mock.assert_not_called_with(1, three=5)
        self.mock.assert_not_called_with()

        with self.assertRaises(AssertionError):
            self.mock.assert_not_called_with(1, 2, three=4)

        self.mock('foo')
        self.mock.assert_not_called_with(1, 2, three=4)  # not the latest call

    def test_assert_not_called_once_with_asserts_one_call_with_args(self):
        self.mock.assert_not_called_once_with(1, 2, three=4)  # 0 times

        self.mock(1, 2, three=4)

        with self.assertRaises(AssertionError):
            self.mock.assert_not_called_once_with(1, 2, three=4)  # 1 time

        self.mock(1, 2, three=4)
        self.mock.assert_not_called_once_with(1, 2, three=4)  # 2 times

    def test_assert_not_any_call_asserts_never_called_with_args(self):
        self.mock.assert_not_any_call(1, 2, three=4)

        self.mock(1, 2, three=4)

        with self.assertRaises(AssertionError):
            self.mock.assert_not_any_call(1, 2, three=4)

        self.mock('foo')

        with self.assertRaises(AssertionError):
            # Even though it's not the latest, it was previously called with
            # these args
            self.mock.assert_not_any_call(1, 2, three=4)
