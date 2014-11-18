.. sacrud documentation master file, created by
   sphinx-quickstart on Fri Jun 27 15:28:02 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SACRUD
======

Overview
--------

sacrud - CRUD interface for SQLAlchemy.

SACRUD will solve your problem of CRUD interface for SQLAlchemy,
by providing `extension for Pyramid <https://github.com/ITCase/pyramid_sacrud>`_ (yet) or use it in pure form.
Unlike classical CRUD interface, `pyramid_sacrud <https://github.com/ITCase/pyramid_sacrud>`_ allows override and flexibly customize interface.
(that is closer to `django.contrib.admin`)

Look how easy it is to use:

.. code-block:: python

    from .models import Groups
    from sacrud.action import CRUD

    data = {'name': 'Electronics',
            'parent_id': '10',}
    group_obj = CRUD(DBSession, Groups, request=data).add()
    print group_obj['obj'].id

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

