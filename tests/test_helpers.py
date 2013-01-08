from unittest2 import TestCase
from mock import patch, Mock, sentinel

from exam.helpers import intercept, rm_f, track, mock_import
from exam.decorators import fixture

from describe import expect


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
        expect(tracker.foo).to == self.foo_mock
        expect(tracker.bar).to == self.bar_mock


class TestMockImport(TestCase):

    def test_is_a_context_manager_that_yields_patched_import(self):
        with mock_import('foo') as mock_foo:
            import foo
            expect(foo).to == mock_foo

    def test_mocks_import_for_packages(self):
        with mock_import('foo.bar.baz') as mock_baz:
            import foo.bar.baz
            expect(foo.bar.baz).to == mock_baz

    @mock_import('foo')
    def test_can_be_used_as_a_decorator_too(self, mock_foo):
        import foo
        expect(foo).to == mock_foo

    @mock_import('foo')
    @mock_import('bar')
    def test_stacked_adds_args_bottom_up(self, mock_bar, mock_foo):
        import foo
        import bar
        expect(mock_bar).to == bar
        expect(mock_foo).to == foo


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
        expect(counter.calls).to == 0
        assert ex.method(sentinel.POSITIONAL_ARGUMENT,
            keyword=sentinel.KEYWORD_ARGUMENT) is sentinel.METHOD_RESULT
        expect(counter.calls).to == 1

        ex.method.unwrap()
        assert ex.method(sentinel.POSITIONAL_ARGUMENT,
            keyword=sentinel.KEYWORD_ARGUMENT) is sentinel.METHOD_RESULT
        expect(counter.calls).to == 1
