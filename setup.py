#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

try:
    import multiprocessing  # NOQA
except ImportError:
    pass

install_requires = ['mock']
lint_requires = ['pep8', 'pyflakes']
tests_require = ['nose', 'unittest2', 'describe']

dependency_links = [
    'https://github.com/jeffh/describe/archive/907b42e4947f88111667a39e23bc5d5e0bf167fd.tar.gz#egg=describe',
]

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name='exam',
    version='0.6.1',
    author='Jeff Pollard',
    author_email='jeff.pollard@gmail.com',
    url='https://github.com/fluxx/exam',
    description='Helpers for better testing.',
    license='MIT',
    packages=find_packages(),
    dependency_links=dependency_links,
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
)
