from mock import sentinel
from unittest2 import TestCase
import itertools

from exam.decorators import fixture, before, after, around, patcher
from exam.cases import Exam

from describe import expect

from dummy import get_thing, get_it


class SimpleTestCase(object):

    def __init__(self):
        self.cleanups = []
        self.setups = 0
        self.teardowns = 0

    def setUp(self):
        self.setups += 1

    def tearDown(self):
        self.teardowns += 1

    def run(self, *args, **kwargs):
        self.state_when_run = list(self.calls)

    def addCleanup(self, func):
        self.cleanups.append(func)


class MyTestCase(Exam, SimpleTestCase):

    @patcher('tests.dummy.thing')
    def dummy_thing(self):
        return sentinel.mock

    dummy_it = patcher('tests.dummy.it', return_value=12)

    def __init__(self):
        self.calls = []
        super(MyTestCase, self).__init__()

    @before
    def append_wine(self):
        self.calls.append('merlot')

    @before
    def append_self(self):
        self.calls.append(type(self))

    @after
    def append_number(self):
        self.calls.append('2 in parent class')

    @after
    def append_person(self):
        self.calls.append('jeff')

    @around
    def fairy_tail(self):
        self.calls.append('hansel')
        yield
        self.calls.append('gretle')


class ExtendedTestCase(MyTestCase):

    @before
    def append_cheese(self):
        self.calls.append('chedder')

    @after
    def append_meat(self):
        self.calls.append('salami')

    @around
    def movies(self):
        self.calls.append('turner')
        yield
        self.calls.append('hootch')

    @before
    def append_self(self):
        self.calls.append(type(self))

    @after
    def append_number(self):
        self.calls.append('two in subclass')


# TODO: Make the subclass checking just be a subclass of the test case
class TestExam(Exam, TestCase):

    @fixture
    def case(self):
        return MyTestCase()

    @fixture
    def subclassed_case(self):
        return ExtendedTestCase()

    @after
    def stop_patchers(self):
        cleanups = (self.case.cleanups, self.subclassed_case.cleanups)

        for cleanup in itertools.chain(*cleanups):
            if hasattr(cleanup.im_self, 'is_local'):  # Is the mock started?
                cleanup()

    @property
    def other_thing(self):
        return get_thing()

    @property
    def other_it(self):
        return get_it()

    def test_before_adds_each_method_to_set_up(self):
        expect(self.case.calls).to == []
        self.case.setUp()
        expect(self.case.calls).to == [MyTestCase, 'merlot']

    def test_after_adds_each_method_to_tear_down(self):
        expect(self.case.calls).to == []
        self.case.tearDown()
        expect(self.case.calls).to == ['jeff', '2 in parent class']

    def test_around_calls_methods_before_and_after_run(self):
        expect(self.case.calls).to == []
        self.case.run()
        expect(self.case.state_when_run).to == ['hansel']
        expect(self.case.calls).to == ['hansel', 'gretle']

    def test_before_works_on_subclasses(self):
        expect(self.subclassed_case.calls).to == []
        self.subclassed_case.setUp()
        expect(self.subclassed_case.calls).to == ['merlot', 'chedder', ExtendedTestCase]

    def test_after_works_on_subclasses(self):
        expect(self.subclassed_case.calls).to == []
        self.subclassed_case.tearDown()
        expect(self.subclassed_case.calls).to == ['jeff', 'salami', 'two in subclass']

    def test_around_works_with_subclasses(self):
        expect(self.subclassed_case.calls).to == []
        self.subclassed_case.run()
        expect(self.subclassed_case.state_when_run).to == ['hansel', 'turner']
        expect(self.subclassed_case.calls).to == ['hansel', 'turner', 'hootch', 'gretle']

    def test_patcher_start_value_is_added_to_case_dict_on_setup(self):
        self.case.setUp()
        expect(self.case.dummy_thing).to == sentinel.mock

    def test_patcher_patches_object_on_setup_and_adds_patcher_to_cleanup(self):
        expect(self.other_thing).to != sentinel.mock
        self.case.setUp()
        expect(self.other_thing).to == sentinel.mock
        [cleanup() for cleanup in self.case.cleanups]
        expect(self.other_thing).to != sentinel.mock

    def test_patcher_lifecycle_works_on_subclasses(self):
        expect(self.other_thing).to != sentinel.mock
        self.subclassed_case.setUp()
        expect(self.other_thing).to == sentinel.mock
        [cleanup() for cleanup in self.subclassed_case.cleanups]
        expect(self.other_thing).to != sentinel.mock

    def test_patcher_patches_with_a_magic_mock_if_no_function_decorated(self):
        expect(self.other_it()).to != 12
        self.case.setUp()
        expect(self.other_it()).to == 12
        self.case.cleanups[0]()
        expect(self.other_thing).to != 12

    def test_calls_super_setup(self):
        expect(self.case.setups).to == 0
        self.case.setUp()
        expect(self.case.setups).to == 1

    def test_calls_super_teardown(self):
        expect(self.case.teardowns).to == 0
        self.case.tearDown()
        expect(self.case.teardowns).to == 1
