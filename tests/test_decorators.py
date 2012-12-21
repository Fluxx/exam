from unittest2 import TestCase
from describe import expect

from exam.decorators import fixture


class Outer(object):

    @classmethod
    def meth(cls):
        return cls, 'from method'


class Dummy(object):

    outside = 'value from outside'

    @fixture
    def number(self):
        return 42

    @fixture
    def obj(self):
        return object()

    inline = fixture(int, 5)
    inline_func = fixture(lambda self: self.outside)
    inline_func_with_args = fixture(lambda *a, **k: (a, k), 1, 2, a=3)
    inline_from_method = fixture(Outer.meth)


class ExtendedDummy(Dummy):

    @fixture
    def number(self):
        return 42 + 42


class TestFixture(TestCase):

    def test_converts_method_to_property(self):
        expect(Dummy().number).to == 42

    def test_caches_property_on_same_instance(self):
        instance = Dummy()
        expect(instance.obj).to.be_equal_to(instance.obj)

    def test_gives_different_object_on_separate_instances(self):
        expect(Dummy().obj).to_not.be_equal_to(Dummy().obj)

    def test_can_be_used_inline_with_a_function(self):
        expect(Dummy().inline_func).to == 'value from outside'

    def test_can_be_used_with_a_callable_that_takes_args(self):
        inst = Dummy()
        expect(inst.inline_func_with_args).to == ((inst, 1, 2), dict(a=3))

    def test_can_be_used_with_class_method(self):
        expect(Dummy().inline_from_method).to == (Outer, 'from method')

    def test_if_passed_type_builds_new_object(self):
        expect(Dummy().inline).to == 5

    def test_override_in_subclass_overrides_value(self):
        expect(ExtendedDummy().number).to == 42 + 42

