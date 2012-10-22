import shutil
import os


def rm_f(path):
    try:
        # Assume it's a directory
        shutil.rmtree(path, ignore_errors=True)
    except OSError:
        # Directory delete failed, so it's likely a file
        os.remove(path)
