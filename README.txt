sacrud
======

sacrud will solve your problem of CRUD interface for SQLAlchemy, by
providing extension for Pyramid or use it in pure form.

Look how easy it is to use with Pyramid:

::

    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("myprojectname:templates")

    from .models import (Model1, Model2, Model3,)
    # add sacrud and project models
    config.include('sacrud.pyramid_ext')
    settings = config.registry.settings
    settings['sacrud.models'] = {'Group1': [Model1, Model2], '': [Model3]}

go to http://localhost:6543/sacrud/


Features
--------

-  Be awesome
-  Read table rows
-  Create and update row
-  Delete row
-  Use sortable table with position field
-  Upload file with FileField
-  Union rows (testing)
-  Custom style

Installation
------------

Install from github:

::

    pip install git+http://github.com/uralbash/sacrud.git

PyPi:

::

    pip install sacrud

Source:

::

    python setup.py install

Contribute
----------

-  Issue Tracker: http://github.com/uralbash/sacrud/issues
-  Source Code: http://github.com/uralbash/sacrud
-  Docs: http://sacrud.readthedocs.org (in process)
-  Demo: http://github.com/uralbash/pyramid\_sacrud\_example

Support
-------

If you are having issues, please let me know. I have a mailing list
located at: sacrud@uralbash.ru

License
-------

The project is licensed under the BSD license.
