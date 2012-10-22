from unittest2 import TestCase
from describe import expect

from exam import fixture


class Dummy(object):

    outside = 'value from outside'

    inline = fixture(lambda self: self.outside)

    @fixture
    def number(self):
        return 42

    @fixture
    def object(self):
        return object()


class TestFixture(TestCase):

    def test_converts_method_to_property(self):
        expect(Dummy().number).to == 42

    def test_caches_property_on_same_instance(self):
        instance = Dummy()
        expect(instance.object).to.be_equal_to(instance.object)

    def test_gives_different_object_on_separate_instances(self):
        expect(Dummy().object).to_not.be_equal_to(Dummy().object)

    def test_can_be_used_with_a_callable(self):
        expect(Dummy().inline).to == 'value from outside'
