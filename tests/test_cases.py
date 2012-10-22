from unittest2 import TestCase

from exam import fixture, before, after, around
from exam.cases import Exam

from describe import expect


class FakeTest(object):

    def run(self, *args, **kwargs):
        self.state_when_run = list(self.calls)


class DummyTest(Exam, FakeTest):

    def __init__(self):
        self.calls = []

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


class TestExam(TestCase):

    @fixture
    def case(self):
        return DummyTest()

    @fixture
    def subclass_case(self):
        return ExtendedDummy()

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
