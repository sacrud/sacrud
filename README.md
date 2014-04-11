[![Build Status](https://travis-ci.org/ITCase/sacrud.svg?branch=master)](https://travis-ci.org/ITCase/sacrud)
[![Coverage Status](https://coveralls.io/repos/ITCase/sacrud/badge.png?branch=master)](https://coveralls.io/r/ITCase/sacrud?branch=master)
[![Stories in Done](https://badge.waffle.io/ITCase/sacrud.png?label=done&title=Done)](http://waffle.io/ITCase/sacrud)
[![Stories in Progress](https://badge.waffle.io/ITCase/sacrud.png?label=in progress&title=In Progress)](http://waffle.io/ITCase/sacrud)

sacrud
======

sacrud will solve your problem of CRUD interface for SQLAlchemy,
by providing extension for Pyramid or use it in pure form. 

Look how easy it is to use with Pyramid:
```python
config.include('pyramid_jinja2')
config.add_jinja2_search_path("myprojectname:templates")

from .models import (Model1, Model2, Model3,)
# add sacrud and project models
config.include('sacrud.pyramid_ext')
settings = config.registry.settings
settings['sacrud.models'] = {'Group1': [Model1, Model2], '': [Model3]}
```

go to http://localhost:6543/sacrud/

and see...

![ScreenShot](https://raw.github.com/uralbash/sacrud/master/docs/img/index.png)

Features
--------

- Be awesome
- Read table rows

![ScreenShot](https://raw.github.com/uralbash/sacrud/master/docs/img/rows.png)

- Create and update row

![ScreenShot](https://raw.github.com/uralbash/sacrud/master/docs/img/edit.png)

- Delete row
- Use sortable table with position field
- Upload file with FileField
- Union rows (testing)
- Customizing interface

Installation
------------

Install from github:

    pip install git+http://github.com/uralbash/sacrud.git

PyPi:

    pip install sacrud

Source:

    python setup.py install

Contribute
----------

- Issue Tracker: http://github.com/uralbash/sacrud/issues
- Source Code: http://github.com/uralbash/sacrud
- Docs: http://sacrud.readthedocs.org (in process)
- Demo: http://github.com/uralbash/pyramid_sacrud_example

Support
-------

If you are having issues, please let me know.
I have a mailing list located at: sacrud@uralbash.ru

License
-------

The project is licensed under the BSD license.

Example
-------
![ScreenShot](https://raw.github.com/uralbash/sacrud/master/docs/img/example.png)
