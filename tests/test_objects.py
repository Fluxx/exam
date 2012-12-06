from unittest2 import TestCase
from describe import expect

from exam.objects import noop


class TestNoOp(TestCase):

    def test_can_be_called_with_anything(self):
        noop()
        noop(1)
        noop(key='val')
        noop(1, key='val')
        noop(1, 2, 3, key='val')
        noop(1, 2, 3, key='val', another='thing')

    def test_returns_none(self):
        expect(noop()).to == None
