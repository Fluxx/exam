from mock import sentinel, MagicMock
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


class DummyTest(Exam, SimpleTestCase):

    @patcher('tests.dummy.thing')
    def dummy_thing(self):
        return sentinel.mock

    dummy_it = patcher('tests.dummy.it', return_value=12)

    def __init__(self):
        self.calls = []
        super(DummyTest, self).__init__()

    @before
    def append_one(self):
        self.calls.append(1)

    @after
    def append_two(self):
        self.calls.append(2)

    @around
    def append_5_then_6(self):
        self.calls.append(5)
        yield
        self.calls.append(6)


class ExtendedDummy(DummyTest):

    @before
    def append_3(self):
        self.calls.append(3)

    @after
    def append_4(self):
        self.calls.append(4)

    @around
    def append_7_then_8(self):
        self.calls.append(7)
        yield
        self.calls.append(8)


# TODO: Make the subclass checking just be a subclass of the test case
class TestExam(Exam, TestCase):

    @fixture
    def case(self):
        return DummyTest()

    @fixture
    def subclass_case(self):
        return ExtendedDummy()

    @after
    def stop_patchers(self):
        cleanups = (self.case.cleanups, self.subclass_case.cleanups)

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
        expect(self.case.calls).to == [1]

    def test_after_adds_each_method_to_tear_down(self):
        expect(self.case.calls).to == []
        self.case.tearDown()
        expect(self.case.calls).to == [2]

    def test_around_calls_methods_before_and_after_run(self):
        expect(self.case.calls).to == []
        self.case.run()
        expect(self.case.state_when_run).to == [5]
        expect(self.case.calls).to == [5, 6]

    def test_before_works_on_subclasses(self):
        expect(self.subclass_case.calls).to == []
        self.subclass_case.setUp()
        expect(self.subclass_case.calls).to == [3, 1]

    def test_after_works_on_subclasses(self):
        expect(self.subclass_case.calls).to == []
        self.subclass_case.tearDown()
        expect(self.subclass_case.calls).to == [4, 2]

    def test_around_works_with_subclasses(self):
        expect(self.subclass_case.calls).to == []
        self.subclass_case.run()
        expect(self.subclass_case.state_when_run).to == [7, 5]
        expect(self.subclass_case.calls).to == [7, 5, 8, 6]

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
        self.subclass_case.setUp()
        expect(self.other_thing).to == sentinel.mock
        [cleanup() for cleanup in self.subclass_case.cleanups]
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
