from tests import TestCase
from mock import patch, Mock, sentinel

from exam.helpers import intercept, rm_f, track, mock_import, call, effect
from exam.decorators import fixture


@patch('exam.helpers.shutil')
class TestRmrf(TestCase):

    path = '/path/to/folder'

    def test_calls_shutil_rmtreee(self, shutil):
        rm_f(self.path)
        shutil.rmtree.assert_called_once_with(self.path, ignore_errors=True)

    @patch('exam.helpers.os')
    def test_on_os_errors_calls_os_remove(self, os, shutil):
        shutil.rmtree.side_effect = OSError
        rm_f(self.path)
        os.remove.assert_called_once_with(self.path)


class TestTrack(TestCase):

    @fixture
    def foo_mock(self):
        return Mock()

    @fixture
    def bar_mock(self):
        return Mock()

    def test_makes_new_mock_and_attaches_each_kwarg_to_it(self):
        tracker = track(foo=self.foo_mock, bar=self.bar_mock)
        self.assertEqual(tracker.foo, self.foo_mock)
        self.assertEqual(tracker.bar, self.bar_mock)


class TestMockImport(TestCase):

    def test_is_a_context_manager_that_yields_patched_import(self):
        with mock_import('foo') as mock_foo:
            import foo
            self.assertEqual(foo, mock_foo)

    def test_mocks_import_for_packages(self):
        with mock_import('foo.bar.baz') as mock_baz:
            import foo.bar.baz
            self.assertEqual(foo.bar.baz, mock_baz)

    @mock_import('foo')
    def test_can_be_used_as_a_decorator_too(self, mock_foo):
        import foo
        self.assertEqual(foo, mock_foo)

    @mock_import('foo')
    @mock_import('bar')
    def test_stacked_adds_args_bottom_up(self, mock_bar, mock_foo):
        import foo
        import bar
        self.assertEqual(mock_bar, bar)
        self.assertEqual(mock_foo, foo)


class TestIntercept(TestCase):

    class Example(object):
        def method(self, positional, keyword):
            return sentinel.METHOD_RESULT

    def test_intercept(self):
        ex = self.Example()

        def counter(positional, keyword):
            assert positional is sentinel.POSITIONAL_ARGUMENT
            assert keyword is sentinel.KEYWORD_ARGUMENT
            result = yield
            assert result is sentinel.METHOD_RESULT
            counter.calls += 1

        counter.calls = 0

        intercept(ex, 'method', counter)
        self.assertEqual(counter.calls, 0)
        assert ex.method(
            sentinel.POSITIONAL_ARGUMENT,
            keyword=sentinel.KEYWORD_ARGUMENT) is sentinel.METHOD_RESULT
        self.assertEqual(counter.calls, 1)

        ex.method.unwrap()
        assert ex.method(
            sentinel.POSITIONAL_ARGUMENT,
            keyword=sentinel.KEYWORD_ARGUMENT) is sentinel.METHOD_RESULT
        self.assertEqual(counter.calls, 1)


class TestEffect(TestCase):

    def test_creates_callable_mapped_to_config_dict(self):
        config = [
            (call(1), 2),
            (call('a'), 3),
            (call(1, b=2), 4),
            (call(c=3), 5)
        ]
        side_effecet = effect(*config)

        self.assertEqual(side_effecet(1), 2)
        self.assertEqual(side_effecet('a'), 3)
        self.assertEqual(side_effecet(1, b=2), 4)
        self.assertEqual(side_effecet(c=3), 5)

    def test_raises_type_error_when_called_with_unknown_args(self):
        side_effect = effect((call(1), 5))
        self.assertRaises(TypeError, side_effect, 'junk')

    def test_can_be_used_with_mutable_data_structs(self):
        side_effect = effect((call([1, 2, 3]), 'list'))
        self.assertEqual(side_effect([1, 2, 3]), 'list')
