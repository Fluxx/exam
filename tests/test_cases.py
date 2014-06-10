from mock import sentinel
from tests import TestCase

from exam.decorators import before, after, around, patcher
from exam.cases import Exam

from tests.dummy import get_thing, get_it, get_prop, ThingClass


class SimpleTestCase(object):
    """
    Meant to act like a typical unittest.TestCase
    """

    def __init__(self):
        self.cleanups = []
        self.setups = 0
        self.teardowns = 0

    def setUp(self):
        self.setups += 1

    def tearDown(self):
        self.teardowns += 1

    def run(self, *args, **kwargs):
        # At this point in time, exam has run its before hooks and has super'd
        # to the TestCase (us), so, capture the state of calls
        self.calls_before_run = list(self.calls)
        self.vars_when_run = vars(self)

    def addCleanup(self, func):
        self.cleanups.append(func)


class BaseTestCase(Exam, SimpleTestCase):
    """
    Meant to act like a test case a typical user would have.
    """
    def __init__(self, *args, **kwargs):
        self.calls = []
        super(BaseTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        """
        Exists only to prove that adding a setUp method to a test case does not
        break Exam.
        """
        pass

    def tearDown(self):
        """
        Exists only to prove that adding a tearDown method to a test case does
        not break Exam.
        """
        pass


class CaseWithBeforeHook(BaseTestCase):

    @before
    def run_before(self):
        self.calls.append('run before')


class CaseWithDecoratedBeforeHook(BaseTestCase):

    def setup_some_state(self):
        self.state = True

    def setup_some_other_state(self):
        self.other_state = True

    @before(setup_some_state)
    def should_have_run_before(self):
        pass

    @before(setup_some_state, setup_some_other_state)
    def should_have_run_both_states(self):
        pass


class SubclassWithBeforeHook(CaseWithBeforeHook):

    @before
    def subclass_run_before(self):
        self.calls.append('subclass run before')


class CaseWithAfterHook(CaseWithBeforeHook):

    @after
    def run_after(self):
        self.calls.append('run after')


class SubclassCaseWithAfterHook(CaseWithAfterHook):

    @after
    def subclass_run_after(self):
        self.calls.append('subclass run after')


class CaseWithAroundHook(BaseTestCase):

    @around
    def run_around(self):
        self.calls.append('run around before')
        yield
        self.calls.append('run around after')


class SubclassCaseWithAroundHook(BaseTestCase):

    @around
    def subclass_run_around(self):
        self.calls.append('subclass run around before')
        yield
        self.calls.append('subclass run around after')


class CaseWithPatcher(BaseTestCase):

    @patcher('tests.dummy.thing')
    def dummy_thing(self):
        return sentinel.mock

    dummy_it = patcher('tests.dummy.it', return_value=12)


class SubclassedCaseWithPatcher(CaseWithPatcher):
    pass


class CaseWithPatcherObject(BaseTestCase):

    @patcher.object(ThingClass, 'prop')
    def dummy_thing(self):
        return 15


class SubclassedCaseWithPatcherObject(CaseWithPatcherObject):
    pass


# TODO: Make the subclass checking just be a subclass of the test case
class TestExam(Exam, TestCase):

    def test_assert_changes_is_asserts_mixin_assert_changes(self):
        from exam.asserts import AssertsMixin
        self.assertEqual(AssertsMixin.assertChanges, Exam.assertChanges)

    def test_before_runs_method_before_test_case(self):
        case = CaseWithBeforeHook()
        self.assertEqual(case.calls, [])
        case.run()
        self.assertEqual(case.calls_before_run, ['run before'])

    def test_before_decorator_runs_func_before_function(self):
        case = CaseWithDecoratedBeforeHook()
        self.assertFalse(hasattr(case, 'state'))
        case.should_have_run_before()
        self.assertTrue(case.state)

    def test_before_decorator_runs_multiple_funcs(self):
        case = CaseWithDecoratedBeforeHook()
        self.assertFalse(hasattr(case, 'state'))
        self.assertFalse(hasattr(case, 'other_state'))
        case.should_have_run_both_states()
        self.assertTrue(case.state)
        self.assertTrue(case.other_state)

    def test_before_decorator_does_not_squash_func_name(self):
        self.assertEqual(
            CaseWithDecoratedBeforeHook.should_have_run_before.__name__,
            'should_have_run_before'
        )

    def test_after_adds_each_method_after_test_case(self):
        case = CaseWithAfterHook()
        self.assertEqual(case.calls, [])
        case.run()
        self.assertEqual(case.calls, ['run before', 'run after'])

    def test_around_calls_methods_before_and_after_run(self):
        case = CaseWithAroundHook()
        self.assertEqual(case.calls, [])
        case.run()
        self.assertEqual(case.calls_before_run, ['run around before'])
        self.assertEqual(case.calls, ['run around before', 'run around after'])

    def test_before_works_on_subclasses(self):
        case = SubclassWithBeforeHook()
        self.assertEqual(case.calls, [])

        case.run()

        # The only concern with ordering here is that the parent class's
        # @before hook fired before it's parents. The actual order of the
        # @before hooks within a level of class is irrelevant.
        self.assertEqual(case.calls, ['run before', 'subclass run before'])

    def test_after_works_on_subclasses(self):
        case = SubclassCaseWithAfterHook()
        self.assertEqual(case.calls, [])

        case.run()

        self.assertEqual(case.calls_before_run, ['run before'])
        self.assertEqual(case.calls,
                         ['run before', 'run after', 'subclass run after'])

    def test_around_works_with_subclasses(self):
        case = SubclassCaseWithAroundHook()
        self.assertEqual(case.calls, [])

        case.run()

        self.assertEqual(case.calls_before_run, ['subclass run around before'])
        self.assertEqual(case.calls,
                         ['subclass run around before',
                          'subclass run around after'])

    def test_patcher_start_value_is_added_to_case_dict_on_run(self):
        case = CaseWithPatcher()
        case.run()
        self.assertEqual(case.vars_when_run['dummy_thing'], sentinel.mock)

    def test_patcher_patches_object_on_setup_and_adds_patcher_to_cleanup(self):
        case = CaseWithPatcher()

        self.assertNotEqual(get_thing(), sentinel.mock)

        case.run()

        self.assertEqual(get_thing(), sentinel.mock)
        [cleanup() for cleanup in case.cleanups]
        self.assertNotEqual(get_thing(), sentinel.mock)

    def test_patcher_lifecycle_works_on_subclasses(self):
        case = SubclassedCaseWithPatcher()

        self.assertNotEqual(get_thing(), sentinel.mock)

        case.run()

        self.assertEqual(get_thing(), sentinel.mock)
        [cleanup() for cleanup in case.cleanups]
        self.assertNotEqual(get_thing(), sentinel.mock)

    def test_patcher_patches_with_a_magic_mock_if_no_function_decorated(self):
        case = CaseWithPatcher()

        self.assertNotEqual(get_it()(), 12)
        case.run()
        self.assertEqual(get_it()(), 12)

        case.cleanups[0]()
        self.assertNotEqual(get_thing(), 12)

    def test_patcher_object_patches_object(self):
        case = CaseWithPatcherObject()
        self.assertNotEqual(get_prop(), 15)

        case.run()
        self.assertEqual(get_prop(), 15)

        [cleanup() for cleanup in case.cleanups]
        self.assertNotEqual(get_prop(), 15)

    def test_patcher_object_works_with_subclasses(self):
        case = SubclassedCaseWithPatcherObject()

        self.assertNotEqual(get_prop(), 15)
        case.run()
        self.assertEqual(get_prop(), 15)

        [cleanup() for cleanup in case.cleanups]
        self.assertNotEqual(get_prop(), 15)
