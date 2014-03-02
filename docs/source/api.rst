API Documentation
=================

Comprehensive reference material for every public API exposed by
:app:`sacrud` is available within this chapter.  The API
documentation is organized alphabetically by module name.

:mod:`sacrud.action`
--------------------------------

Action
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: sacrud.action
.. autofunction:: sacrud.action.list
.. autofunction:: sacrud.action.create
.. autofunction:: sacrud.action.read
.. autofunction:: sacrud.action.update
.. autofunction:: sacrud.action.delete

:mod:`sacrud.common`
--------------------------------

Common
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: sacrud.common
.. autofunction:: sacrud.common.sa_helpers.get_pk
.. autofunction:: sacrud.common.sa_helpers.get_relations
.. autofunction:: sacrud.common.sa_helpers.delete_fileobj
.. autofunction:: sacrud.common.sa_helpers.check_type
.. autofunction:: sacrud.common.sa_helper.store_file

:mod:`sacrud.exttype`
--------------------------------

Extension types
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: sacrud.exttype
.. autoclass:: FileStore
    :members:
    :inherited-members:

