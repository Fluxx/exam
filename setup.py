#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

try:
    import multiprocessing  # NOQA
except ImportError:
    pass

install_requires = ['mock']
lint_requires = ['pep8', 'pyflakes']
tests_require = ['nose']

if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name='exam',
    version='0.10.6',
    author='Jeff Pollard',
    author_email='jeff.pollard@gmail.com',
    url='https://github.com/fluxx/exam',
    description='Helpers for better testing.',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    extras_require={
        'test': tests_require,
        'all': install_requires + tests_require,
        'docs': ['sphinx'] + tests_require,
        'lint': lint_requires
    },
    zip_safe=False,
    test_suite='nose.collector',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],
)
