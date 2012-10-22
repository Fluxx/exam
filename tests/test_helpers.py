from unittest2 import TestCase
from mock import patch

from exam.helpers import rm_f


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
