import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

here = os.path.dirname(os.path.realpath(__file__))


def read(name):
    with open(os.path.join(here, name)) as f:
        return f.read()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = [
            '--cov=sacrud'
        ]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='sacrud',
    version='0.3.4.dev1',
    url='http://github.com/ITCase/sacrud/',
    author='Svintsov Dmitry',
    author_email='root@uralbash.ru',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="pytest",
    cmdclass={'test': PyTest},
    license="MIT",
    description='CRUD interface for SQLAlchemy.',
    long_description=read('README.rst'),
    install_requires=read('requirements.txt'),
    tests_require=read('requirements.txt') + read('requirements-test.txt'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Database",
        "Topic :: Internet",
    ],
    keywords=['crud', 'database', 'sqlalchemy', 'marshmallow'],
)
