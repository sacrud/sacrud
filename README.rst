|Build Status| |Coverage Status| |Stories in Progress| |PyPI|

sacrud
======

SACRUD will solve your problem of CRUD interface for SQLAlchemy.
Originally created for
`pyramid_sacrud <https://github.com/sacrud/pyramid_sacrud/blob/master/pyramid_sacrud/views/CRUD.py>`_
, but then in a separate project

Look how easy it is to use:

**CREATE**

.. code:: python

    from .models import DBSession, Groups
    from sacrud.action import CRUD

    data = {'name': 'Electronics',
            'parent_id': '10',}
    group_obj = CRUD(DBSession, Groups).create(data)
    print(group_obj.name)

If the entry already exists, just add the option ``update=True``.

.. code:: python

    from .models import DBSession, Groups
    from sacrud.action import CRUD

    data = {'id': 6,  # existing entry
            'name': 'Electronics',
            'parent_id': '10',}
    group_obj = CRUD(DBSession, Groups).create(data, update=True)
    print(group_obj.name)

**READ**

.. code:: python

    from .models import DBSession, Groups
    from sacrud.action import CRUD

    group_obj = CRUD(DBSession, Groups).read()
    print(group_obj.name)

**UPDATE**

.. code:: python

    from .models import DBSession, Groups
    from sacrud.action import CRUD

    group_obj = CRUD(DBSession, Groups).update(1, {'name': 'Chemistry'})
    print(group_obj.name)

**DELETE**

.. code:: python

    from .models import DBSession, Groups
    from sacrud.action import CRUD

    CRUD(DBSession, Groups).delete(1)

**M2M and M2O data**

For adding multiple data for m2m or m2o use endinng `[]`, ex.:

.. code-block:: python

    from .models import DBSession, Users
    from sacrud.action import CRUD

    CRUD(DBSession, Users).create(
        {'name': 'Vasya', 'sex': 1,
         'groups[]': ['["id", 1]', '["id", 2]']}
    )

It support composit primary key.

**Wraps your SQLAlchemy session**

.. code:: python

     from sqlalchemy.orm import scoped_session, sessionmaker
     from sacrud import CRUDSession

     Session = scoped_session(sessionmaker(class_=CRUDSession))
     DBSession = Session()
     DBSession.sacrud(User).delete(1)

**Wraps your zope.sqlalchemy session**

.. code:: python

     from sqlalchemy.orm import scoped_session, sessionmaker
     from zope.sqlalchemy import ZopeTransactionExtension
     from sacrud import crud_sessionmaker

     DBSession = crud_sessionmaker(scoped_session(
         sessionmaker(extension=ZopeTransactionExtension())))
     DBSession.sacrud(User).delete(1)

Now CRUD available from DBSession.

.. code:: python

    group_obj = DBSession.sacrud(Groups).create(data)
    print(group_obj.name)


Installation
------------

Install from github:

::

    pip install git+http://github.com/sacrud/sacrud.git

PyPi:

::

    pip install sacrud

Source:

::

    python setup.py install

Contribute
----------

-  Issue Tracker: http://github.com/sacrud/sacrud/issues
-  Source Code: http://github.com/sacrud/sacrud
-  Docs: http://sacrud.readthedocs.org

Support
-------

If you are having issues, please let me know. I have a mailing list
located at sacrud@uralbash.ru and IRC channel #sacrud

License
-------

The project is licensed under the MIT license.

.. |Build Status| image:: https://travis-ci.org/sacrud/sacrud.svg?branch=master
   :target: https://travis-ci.org/sacrud/sacrud
.. |Coverage Status| image:: https://coveralls.io/repos/sacrud/sacrud/badge.png?branch=master
   :target: https://coveralls.io/r/sacrud/sacrud?branch=master
.. |Stories in Progress| image:: https://badge.waffle.io/sacrud/sacrud.png?label=in%20progress&title=In%20Progress
   :target: http://waffle.io/sacrud/sacrud
.. |PyPI| image:: http://img.shields.io/pypi/dm/sacrud.svg
   :target: https://pypi.python.org/pypi/sacrud/
