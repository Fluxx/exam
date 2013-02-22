from mock import sentinel
from unittest2 import TestCase

from exam.decorators import before, after, around, patcher
from exam.cases import Exam

from describe import expect

from dummy import get_thing, get_it


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


class CaseWithBeforeHook(BaseTestCase):

    @before
    def run_before(self):
        self.calls.append('run before')


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


# TODO: Make the subclass checking just be a subclass of the test case
class TestExam(Exam, TestCase):

    def test_assert_changes_is_asserts_mixin_assert_changes(self):
        from exam.asserts import AssertsMixin
        expect(AssertsMixin.assertChanges, Exam.assertChanges)

    def test_before_runs_method_before_test_case(self):
        case = CaseWithBeforeHook()
        expect(case.calls).to == []
        case.run()
        expect(case.calls_before_run).to == ['run before']

    def test_after_adds_each_method_after_test_case(self):
        case = CaseWithAfterHook()
        expect(case.calls).to == []
        case.run()
        expect(case.calls).to == ['run before', 'run after']

    def test_around_calls_methods_before_and_after_run(self):
        case = CaseWithAroundHook()
        expect(case.calls).to == []
        case.run()
        expect(case.calls_before_run).to == ['run around before']
        expect(case.calls).to == ['run around before', 'run around after']

    def test_before_works_on_subclasses(self):
        case = SubclassWithBeforeHook()
        expect(case.calls).to == []

        case.run()

        # The only concern with ordering here is that the parent class's @before
        # hook fired before it's parents.  The actual order of the @before hooks
        # within a level of class is irrelevant.
        expect(case.calls).to == ['run before', 'subclass run before']

    def test_after_works_on_subclasses(self):
        case = SubclassCaseWithAfterHook()
        expect(case.calls).to == []

        case.run()

        expect(case.calls_before_run).to == ['run before']
        expect(case.calls).to == ['run before', 'run after', 'subclass run after']

    def test_around_works_with_subclasses(self):
        case = SubclassCaseWithAroundHook()
        expect(case.calls).to == []

        case.run()

        expect(case.calls_before_run).to == ['subclass run around before']
        expect(case.calls).to == ['subclass run around before', 'subclass run around after']

    def test_patcher_start_value_is_added_to_case_dict_on_run(self):
        case = CaseWithPatcher()
        case.run()
        expect(case.vars_when_run['dummy_thing']).to == sentinel.mock

    def test_patcher_patches_object_on_setup_and_adds_patcher_to_cleanup(self):
        case = CaseWithPatcher()

        expect(get_thing()).to != sentinel.mock

        case.run()

        expect(get_thing()).to == sentinel.mock
        [cleanup() for cleanup in case.cleanups]
        expect(get_thing()).to != sentinel.mock

    def test_patcher_lifecycle_works_on_subclasses(self):
        case = SubclassedCaseWithPatcher()

        expect(get_thing()).to != sentinel.mock

        case.run()

        expect(get_thing()).to == sentinel.mock
        [cleanup() for cleanup in case.cleanups]
        expect(get_thing()).to != sentinel.mock

    def test_patcher_patches_with_a_magic_mock_if_no_function_decorated(self):
        case = CaseWithPatcher()

        expect(get_it()()).to != 12
        case.run()
        expect(get_it()()).to == 12

        case.cleanups[0]()
        expect(get_thing()).to != 12
