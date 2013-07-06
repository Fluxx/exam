from __future__ import absolute_import

from mock import Mock as BaseMock
from mock import call


class Mock(BaseMock):

    def assert_called(self):
        assert self.called

    def assert_not_called(self):
        assert not self.called

    def assert_not_called_with(self, *args, **kwargs):
        assert not call(*args, **kwargs) == self.call_args

    def assert_not_called_once_with(self, *args, **kwargs):
        assert len(self.__calls_matching(*args, **kwargs)) is not 1

    def assert_not_any_call(self, *args, **kwargs):
        assert len(self.__calls_matching(*args, **kwargs)) is 0

    def __calls_matching(self, *args, **kwargs):
        calls_match = lambda other_call: call(*args, **kwargs) == other_call
        return list(filter(calls_match, self.call_args_list))
