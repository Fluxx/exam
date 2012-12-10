from describe import expect
from mock import sentinel
from unittest2 import TestCase

from exam.objects import always, noop


class TestAlways(TestCase):

    def test_always_returns_identity(self):
        fn = always(sentinel.RESULT_VALUE)
        assert fn() is sentinel.RESULT_VALUE
        assert fn(1, key='value') is sentinel.RESULT_VALUE

    def test_can_be_called_with_anything(self):
        noop()
        noop(1)
        noop(key='val')
        noop(1, key='val')
        noop(1, 2, 3, key='val')
        noop(1, 2, 3, key='val', another='thing')

    def test_returns_none(self):
        expect(noop()).to == None
