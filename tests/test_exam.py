from tests import TestCase


import exam


class TestExam(TestCase):

    DECORATORS = ('fixture', 'before', 'after', 'around', 'patcher')

    def test_exam_is_cases_exam(self):
        from exam.cases import Exam
        self.assertEqual(exam.Exam, Exam)

    def test_imports_all_the_decorators(self):
        import exam.decorators

        for decorator in self.DECORATORS:
            from_decorators = getattr(exam.decorators, decorator)
            from_root = getattr(exam, decorator)

            self.assertEqual(from_root, from_decorators)
