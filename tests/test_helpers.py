from unittest2 import TestCase
from mock import patch, Mock

from exam.helpers import rm_f, track
from exam import fixture

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
