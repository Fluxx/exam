from unittest2 import TestCase

from exam import fixture, before, after
from exam.cases import Exam

from describe import expect


class DummyTest(Exam):

    def __init__(self):
        self.calls = []

    @before
    def append_one(self):
        print 'in append_one', self
        self.calls.append(1)

    @after
    def append_two(self):
        self.calls.append(2)


class ExtendedDummy(DummyTest):

    @before
    def append_3(self):
        self.calls.append(3)

    @after
    def append_4(self):
        self.calls.append(4)


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

    def test_before_works_on_subclasses(self):
        expect(self.subclass_case.calls).to == []
        self.subclass_case.setUp()
        expect(self.subclass_case.calls).to == [3, 1]

    def test_after_works_on_subclasses(self):
        expect(self.subclass_case.calls).to == []
        self.subclass_case.tearDown()
        expect(self.subclass_case.calls).to == [4, 2]
