from unittest2 import TestCase

from describe import expect


import exam


class TestExam(TestCase):

    DECORATORS = ('fixture', 'before', 'after', 'around', 'patcher')

    def test_exam_is_cases_exam(self):
        from exam.cases import Exam
        expect(exam.Exam).to == Exam

    def test_imports_all_the_decorators(self):
        import exam.decorators

        for decorator in self.DECORATORS:
            from_decorators = getattr(exam.decorators, decorator)
            from_root = getattr(exam, decorator)

            expect(from_root).to == from_decorators
