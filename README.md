[![Build Status](https://travis-ci.org/ITCase/sacrud.svg?branch=master)](https://travis-ci.org/ITCase/sacrud)
[![Coverage Status](https://coveralls.io/repos/ITCase/sacrud/badge.png?branch=master)](https://coveralls.io/r/ITCase/sacrud?branch=master)
[![Stories in Progress](https://badge.waffle.io/ITCase/sacrud.png?label=in progress&title=In Progress)](http://waffle.io/ITCase/sacrud)
[![PyPI](http://img.shields.io/pypi/dm/sacrud.svg)](https://pypi.python.org/pypi/sacrud/)

sacrud
======

sacrud - CRUD interface for SQLAlchemy with Pyramid gateway.

SACRUD will solve your problem of CRUD interface for SQLAlchemy, by providing extension for Pyramid (yet) or use it in pure form. Unlike classical CRUD interface, sacrud allows override and flexibly customize interface. (that is closer to django.contrib.admin)

Look how easy it is to use with Pyramid:
```python
config.include('pyramid_jinja2')
config.add_jinja2_search_path("myprojectname:templates")

from .models import (Model1, Model2, Model3,)
# add sacrud and project models
config.include('sacrud.pyramid_ext')
settings = config.registry.settings
settings['sacrud.models'] = {'Group1': {
                                'tables': [Model1, Model2],
                                'position': 1,},
                             'Group2': {
                                'tables': [Model3],
                                'position': 4,}
                            }
```

go to http://localhost:6543/sacrud/

and see...

![ScreenShot](https://raw.github.com/uralbash/sacrud/master/docs/_static/img/dashboard.png)

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
