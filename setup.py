#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

from exam import __version__

try:
    import multiprocessing
except ImportError:
    pass

install_requires = []
lint_requires = ['pep8', 'pyflakes']
tests_require = ['mock', 'nose', 'unittest2', 'describe==1.0.0beta1']

dependency_links = [
    'https://github.com/jeffh/describe/tarball/dev#egg=describe'
]

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name='exam',
    version=__version__,
    author='Jeff Pollard',
    author_email='jeff.pollard@gmail.com',
    url='https://github.com/fluxx/exam',
    description='Helpers for better testing.',
    license='MIT',
    packages=find_packages(),
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