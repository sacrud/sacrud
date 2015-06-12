import os

from setuptools import find_packages, setup

here = os.path.dirname(os.path.realpath(__file__))


def read(name):
    with open(os.path.join(here, name)) as f:
        return f.read()

setup(
    name='sacrud',
    version='0.2.9',
    url='http://github.com/ITCase/sacrud/',
    author='Svintsov Dmitry',
    author_email='root@uralbash.ru',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    license="MIT",
    description='SQLAlchemy CRUD.',
    long_description=read('README.rst'),
    install_requires=read('requirements.txt'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Database",
        "Topic :: Internet",
    ],
    keywords=['crud', 'database', 'sqlalchemy'],
)
