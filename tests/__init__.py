import sys


if sys.version_info < (2, 7):
    from unittest2 import TestCase  # NOQA
else:
    from unittest import TestCase  # NOQA
