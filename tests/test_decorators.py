from tests import TestCase

from exam.decorators import fixture


class Outer(object):

    @classmethod
    def meth(cls):
        return cls, 'from method'

    @classmethod
    def reflective_meth(cls, arg):
        return cls, arg


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

    inline_from_method_with_arg_1 = fixture(Outer.reflective_meth, 1)
    inline_from_method_with_arg_2 = fixture(Outer.reflective_meth, 2)


class ExtendedDummy(Dummy):

    @fixture
    def number(self):
        return 42 + 42


class TestFixture(TestCase):

    def test_converts_method_to_property(self):
        self.assertEqual(Dummy().number, 42)

    def test_caches_property_on_same_instance(self):
        instance = Dummy()
        self.assertEqual(instance.obj, instance.obj)

    def test_gives_different_object_on_separate_instances(self):
        self.assertNotEqual(Dummy().obj, Dummy().obj)

    def test_can_be_used_inline_with_a_function(self):
        self.assertEqual(Dummy().inline_func, 'value from outside')

    def test_can_be_used_with_a_callable_that_takes_args(self):
        inst = Dummy()
        self.assertEqual(inst.inline_func_with_args, ((inst, 1, 2), dict(a=3)))

    def test_can_be_used_with_class_method(self):
        self.assertEqual(Dummy().inline_from_method, (Outer, 'from method'))

    def test_if_passed_type_builds_new_object(self):
        self.assertEqual(Dummy().inline, 5)

    def test_override_in_subclass_overrides_value(self):
        self.assertEqual(ExtendedDummy().number, 42 + 42)

    def test_captures_identical_funcs_with_args_separatly(self):
        instance = Dummy()

        first = instance.inline_from_method_with_arg_1
        second = instance.inline_from_method_with_arg_2

        self.assertNotEqual(first, second)

    def test_clas_access_returns_fixture_itself(self):
        self.assertEqual(getattr(Dummy, 'number'), Dummy.number)
