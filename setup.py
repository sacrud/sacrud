import os
from setuptools import setup, find_packages

this = os.path.dirname(os.path.realpath(__file__))


def readme():
    with open(os.path.join(this, 'README.rst')) as f:
        return f.read()


setup(
    name='sacrud',
    version='0.2.1',
    url='http://github.com/ITCase/sacrud/',
    author='Svintsov Dmitry',
    author_email='root@uralbash.ru',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    license="MIT",
    description='SQLAlchemy CRUD.',
    long_description=readme(),
    install_requires=[
        "sqlalchemy",
        "transaction",
        'zope.sqlalchemy',
        'webhelpers',
        'webtest',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Framework :: Pyramid ",
        "Framework :: Flask",
        "Topic :: Internet",
        "Topic :: Database",
    ],
)
