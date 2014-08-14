[![Build Status](https://travis-ci.org/ITCase/sacrud.svg?branch=master)](https://travis-ci.org/ITCase/sacrud)
[![Coverage Status](https://coveralls.io/repos/ITCase/sacrud/badge.png?branch=master)](https://coveralls.io/r/ITCase/sacrud?branch=master)
[![Stories in Progress](https://badge.waffle.io/ITCase/sacrud.png?label=in progress&title=In Progress)](http://waffle.io/ITCase/sacrud)
[![PyPI](http://img.shields.io/pypi/dm/sacrud.svg)](https://pypi.python.org/pypi/sacrud/)

sacrud
======

sacrud - CRUD interface for SQLAlchemy.

SACRUD will solve your problem of CRUD interface for SQLAlchemy, by providing [extension for Pyramid](https://github.com/ITCase/pyramid_sacrud) (yet) or use it in pure form. Unlike classical CRUD interface, [pyramid_sacrud](https://github.com/ITCase/pyramid_sacrud) allows override and flexibly customize interface. (that is closer to django.contrib.admin)

Look how easy it is to use:
```python
from .models import Groups
from sacrud.action import CRUD

data = {'name': 'Electronics',
        'parent_id': '10',}
group_obj = CRUD(DBSession, Groups, request=data).add()
print group_obj.id
```

Installation
------------

Install from github:

    pip install git+http://github.com/ITCase/sacrud.git

PyPi:

    pip install sacrud

Source:

    python setup.py install

Contribute
----------

- Issue Tracker: http://github.com/ITCase/sacrud/issues
- Source Code: http://github.com/ITCase/sacrud
- Docs: http://sacrud.readthedocs.org
- Demo: http://github.com/ITCase/pyramid_sacrud_example

Support
-------

If you are having issues, please let me know.
I have a mailing list located at: sacrud@uralbash.ru

License
-------

The project is licensed under the MIT license.
