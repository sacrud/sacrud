Usage :mod:`sacrud`
===================

Wraps your SQLAlchemy session
-----------------------------

.. code-block:: python

     from sqlalchemy.orm import scoped_session, sessionmaker
     from sacrud import CRUDSession

     Session = scoped_session(sessionmaker(class_=CRUDSession))
     DBSession = Session()
     DBSession.sacrud(User).delete(1)

Now CRUD available from DBSession.

.. code:: python

    group_obj = DBSession.sacrud(Groups).create(data)
    print(group_obj.name)

Wraps your zope.sqlalchemy session
----------------------------------

.. code-block:: python

     from sqlalchemy.orm import scoped_session, sessionmaker
     from zope.sqlalchemy import ZopeTransactionExtension
     from sacrud import crud_sessionmaker

     DBSession = crud_sessionmaker(scoped_session(
         sessionmaker(extension=ZopeTransactionExtension())))
     DBSession.sacrud(User).delete(1)

Now CRUD available from DBSession.

.. code-block:: python

    group_obj = DBSession.sacrud(Groups).create(data)
    print(group_obj.name)

CREATE action
-------------

.. code-block:: python
    :caption: CREATE action

    data = {'name': 'Electronics',
            'parent_id': '10'}
    group_obj = DBSession.sacrud(Groups).create(data)
    print(group_obj.name)

If the entry already exists, just add the option ``update=True``.

.. code-block:: python
    :caption: CREATE action with option ``update=True``

    from .models import DBSession, Groups
    from sacrud.action import CRUD

    data = {'id': 6,  # existing entry
            'name': 'Electronics',
            'parent_id': '10',}
    group_obj = CRUD(DBSession, Groups).create(data, update=True)
    print(group_obj.name)

You can pass JSON data:

.. code-block:: python
    :caption: CREATE action with JSON data

    from .models import DBSession, Groups
    from sacrud.action import CRUD

    data = '''
    {
       "id": 6,
       "name": "Electronics",
       "parent_id": "10"
    }
    '''
    group_obj = CRUD(DBSession, Groups).create(data, update=True)
    print(group_obj.name)

For more details see:

* :ref:`API`
* :py:mod:`sacrud.action.CRUD`
* :py:class:`sacrud.tests.test_action.CreateTest`


READ action
-----------

.. code-block:: python
   :caption: All users

   DBSession.sacrud(Users).read()

.. code-block:: python
   :caption: SELECT one row with composite primary key

   DBSession.sacrud(User2Groups).read({'user_id': 4, 'group_id': 2})

.. code-block:: python
   :caption: SELECT several rows with composit primary key

   primary_keys =[
      {'user_id': 4, 'group_id': 2},
      {'user_id': 4, 'group_id': 3},
      {'user_id': 1, 'group_id': 1},
      {'user_id': 19, 'group_id': 2}
   ]
   rows = DBSession.sacrud(User2Groups).read(*primary_keys)

.. code-block:: python
   :caption: Delete rows

   rows.delete(synchronize_session=False)

.. code-block:: python
   :caption: Same, but work with only not composite primary key

   DBSession.sacrud(Users).read((5, 10))   # as list
   DBSession.sacrud(Users).read(5, "1", 2) # as *args
   DBSession.sacrud(Users).read(42)        # single

You can pass JSON data:

.. code-block:: python
   :caption: JSON primary keys in READ action

   # Composite primary_key
   DBSession.sacrud(User2Groups).read({'user_id': 4, 'group_id': 2})
   primary_keys =[
      {'user_id': 4, 'group_id': 2},
      {'user_id': 4, 'group_id': 3},
      {'user_id': 1, 'group_id': 1},
      {'user_id': 19, 'group_id': 2}
   ]
   rows = DBSession.sacrud(User2Groups).read(*primary_keys)

For more details see:

* :ref:`API`
* :py:mod:`sacrud.action.CRUD`
* :py:class:`sacrud.tests.test_action.ReadTest`

UPDATE action
-------------

.. code-block:: python
   :caption: UPDATE action

   DBSession.sacrud(Users).update(1, {'name': 'Petya'})
   DBSession.sacrud(Users).update('1', {'name': 'Petya'})
   DBSession.sacrud(User2Groups).update({'user_id': 4, 'group_id': 2},
                                        {'group_id': 1})

.. code-block:: python
   :caption: UPDATE action with JSON data

   DBSession.sacrud(Users).update(1, '{"name": "Petya"}')
   DBSession.sacrud(User2Groups).update(
      '{"user_id": 4, "group_id": 2}',
      '{"group_id": 1}'
   )

For more details see:

* :ref:`API`
* :mod:`sacrud.action.CRUD`
* :py:class:`sacrud.tests.test_action.UpdateTest`


DELETE action
-------------

.. code-block:: python
   :caption: DELETE action

   DBSession.sacrud(Users).delete(1)
   DBSession.sacrud(Users).delete('1')
   DBSession.sacrud(User2Groups).delete({'user_id': 4, 'group_id': 2})

.. code-block:: python
   :caption: DELETE action with JSON composit key

   DBSession.sacrud(User2Groups).delete('{"user_id": 4, "group_id": 2}')

For more details see:

* :ref:`API`
* :mod:`sacrud.action.CRUD`
* :py:class:`sacrud.tests.test_action.DeleteTest`

Example projects use plain `sacrud`
-----------------------------------

`pyramid_sacrud <https://github.com/ITCase/pyramid_sacrud>`_

.. literalinclude:: _pyramid_sacrud/pyramid_sacrud/views/CRUD.py
   :linenos:
   :language: python
   :pyobject: Delete
   :emphasize-lines: 6-7
