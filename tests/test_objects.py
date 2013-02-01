from describe import expect
from mock import sentinel
from unittest2 import TestCase

from exam.objects import always, noop, call, effect


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


class TestCall(TestCase):

    def test_records_and_checks_equality_on_calls(self):
        expect(call(1)).to == call(1)
        expect(call(1)).to != call(2)
        expect(call(1, 2)).to == call(1, 2)
        expect(call(1, 2, a=5)).to == call(1, 2, a=5)

    def test_works_with_mutable_types(self):
        expect(call([1])).to == call([1])


class TestEffect(TestCase):

    def test_creates_callable_mapped_to_config_dict(self):
        config = [
            (call(1), 2),
            (call('a'), 3),
            (call(1, b=2), 4),
            (call(c=3), 5)
        ]
        side_effecet = effect(*config)

        expect(side_effecet(1)).to == 2
        expect(side_effecet('a')).to == 3
        expect(side_effecet(1, b=2)).to == 4
        expect(side_effecet(c=3)).to == 5

    def test_raises_type_error_when_called_with_unknown_args(self):
        side_effect = effect((call(1), 5))
        self.assertRaises(TypeError, side_effect, 'junk')

    def test_can_be_used_with_mutable_data_structs(self):
        side_effect = effect((call([1, 2, 3]), 'list'))
        expect(side_effect([1, 2, 3])).to == 'list'
