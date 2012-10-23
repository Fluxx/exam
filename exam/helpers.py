import shutil
import os
from mock import MagicMock


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
