.. sacrud documentation master file, created by
   sphinx-quickstart on Fri Jun 27 15:28:02 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SACRUD
======

Overview
--------

SACRUD will solve your problem of CRUD interface for SQLAlchemy.
Originally created for
`pyramid_sacrud <https://github.com/ITCase/pyramid_sacrud/blob/master/pyramid_sacrud/views/CRUD.py>`_
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

Usage
-----

.. toctree::
   :maxdepth: 3

   install
   plain_usage
   api

.. include:: contribute.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

