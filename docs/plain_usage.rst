Usage `sacrud`
==============

Wraps your SQLAlchemy session
-----------------------------

.. code:: python

     from sqlalchemy.orm import scoped_session, sessionmaker
     from sacrud import crud_sessionmaker

     DBSession = crud_sessionmaker(scoped_session(sessionmaker()))
     help(DBSession.sacrud)

Now CRUD available from DBSession.

CREATE action
-------------

.. code-block:: python
    :linenos:

    data = {'name': 'Electronics',
            'parent_id': '10'}
    group_obj = DBSession.sacrud(Groups).create(data)
    print(group_obj.name)

For more details see:

* :ref:`API`
* :py:mod:`sacrud.action.CRUD`
* :py:class:`sacrud.tests.test_action.CreateTest`


READ action
-----------

.. code-block:: python
   :linenos:

   # All users
   DBSession.sacrud(Users).read()

   # Composite primary_key
   DBSession.sacrud(User2Groups).read({'user_id': 4, 'group_id': 2})
   DBSession.sacrud(User2Groups).read(
     pk=[{'user_id': 4, 'group_id': 2},
         {'user_id': 4, 'group_id': 3},
         {'user_id': 1, 'group_id': 1},
         {'user_id': 19, 'group_id': 2}]
    )

   # Same, but work with only not composite primary key
   DBSession.sacrud(Users).read((5, 10))   # as list
   DBSession.sacrud(Users).read(5, "1", 2) # as *args
   DBSession.sacrud(Users).read(42)        # single

For more details see:

* :ref:`API`
* :py:mod:`sacrud.action.CRUD`
* :py:class:`sacrud.tests.test_action.ReadTest`

UPDATE action
-------------

.. code-block:: python
   :linenos:

   DBSession.sacrud(Users).update(1, {'name': 'Petya'})
   DBSession.sacrud(Users).update('1', {'name': 'Petya'})
   DBSession.sacrud(User2Groups).update({'user_id': 4, 'group_id': 2},
                                        {'group_id': 1})

For more details see:

* :ref:`API`
* :mod:`sacrud.action.CRUD`
* :py:class:`sacrud.tests.test_action.UpdateTest`


DELETE action
-------------

.. code-block:: python
   :linenos:

   DBSession.sacrud(Users).delete(1)
   DBSession.sacrud(Users).delete('1')
   DBSession.sacrud(User2Groups).delete({'user_id': 4, 'group_id': 2})

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
