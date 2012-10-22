from unittest2 import TestCase
from describe import expect

from exam.objects import no_op


class TestNoOp(TestCase):

    def test_can_be_called_with_anything(self):
        no_op()
        no_op(1)
        no_op(key='val')
        no_op(1, key='val')
        no_op(1, 2, 3, key='val')
        no_op(1, 2, 3, key='val', another='thing')

    def test_returns_none(self):
        expect(no_op()).to == None
