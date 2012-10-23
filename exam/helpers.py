import shutil
import os
import functools

from mock import MagicMock, patch


def rm_f(path):
    try:
        # Assume it's a directory
        shutil.rmtree(path, ignore_errors=True)
    except OSError:
        # Directory delete failed, so it's likely a file
        os.remove(path)


def track(**mocks):
    tracker = MagicMock()

    for name, mocker in mocks.items():
        tracker.attach_mock(mocker, name)

    return tracker


class mock_import(patch.dict):

    FROM_X_GET_Y = lambda s, x, y: getattr(x, y)

    def __init__(self, path):
        self.mock = MagicMock()
        self.path = path
        self.modules = {self.base: self.mock}

        for i in range(len(self.remainder)):
            tail_parts = self.remainder[0:i + 1]
            key = '.'.join([self.base] + tail_parts)
            reduction = reduce(self.FROM_X_GET_Y, tail_parts, self.mock)
            self.modules[key] = reduction

        super(mock_import, self).__init__('sys.modules', self.modules)

    @property
    def base(self):
        return self.path.split('.')[0]

    @property
    def remainder(self):
        return self.path.split('.')[1:]

    def __enter__(self):
        super(mock_import, self).__enter__()
        return self.modules[self.path]

    def __call__(self, func):
        super(mock_import, self).__call__(func)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            args = list(args)
            args.append(self.modules[self.path])

            with self:
                func(*args, **kwargs)

        return inner
