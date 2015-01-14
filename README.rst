|Build Status| |Coverage Status| |Stories in Progress| |PyPI|

sacrud
======

sacrud - CRUD interface for SQLAlchemy.

SACRUD will solve your problem of CRUD interface for SQLAlchemy, by
providing `extension for Pyramid`_ (yet) or use it in pure form. Unlike
classical CRUD interface, `pyramid\_sacrud`_ allows override and
flexibly customize interface. (that is closer to django.contrib.admin)

Look how easy it is to use:

.. code:: python

    from .models import Groups
    from sacrud.action import CRUD

    data = {'name': 'Electronics',
            'parent_id': '10',}
    group_obj = CRUD(DBSession, Groups, request=data).add()
    print group_obj['obj'].id

Installation
------------

Install from github:

::

    pip install git+http://github.com/ITCase/sacrud.git

PyPi:

::

    pip install sacrud

Source:

::

    python setup.py install

Contribute
----------

-  Issue Tracker: http://github.com/ITCase/sacrud/issues
-  Source Code: http://github.com/ITCase/sacrud
-  Docs: http://sacrud.readthedocs.org
-  Demo: http://github.com/ITCase/pyramid\_sacrud\_example

Support
-------

If you are having issues, please let me know. I have a mailing list
located at sacrud@uralbash.ru and IRC channel #sacrud

License
-------

The project is licensed under the MIT license.

.. _extension for Pyramid: https://github.com/ITCase/pyramid_sacrud
.. _pyramid\_sacrud: https://github.com/ITCase/pyramid_sacrud

.. |Build Status| image:: https://travis-ci.org/ITCase/sacrud.svg?branch=master
   :target: https://travis-ci.org/ITCase/sacrud
.. |Coverage Status| image:: https://coveralls.io/repos/ITCase/sacrud/badge.png?branch=master
   :target: https://coveralls.io/r/ITCase/sacrud?branch=master
.. |Stories in Progress| image:: https://badge.waffle.io/ITCase/sacrud.png?label=in%20progress&title=In%20Progress
   :target: http://waffle.io/ITCase/sacrud
.. |PyPI| image:: http://img.shields.io/pypi/dm/sacrud.svg
   :target: https://pypi.python.org/pypi/sacrud/
