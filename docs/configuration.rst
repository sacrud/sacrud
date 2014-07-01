Application Configuration for Pyramid
=====================================

Initialize
----------

`sacrud` work with Jinja2 template renderer

.. note::
    work only with pyramid_jinja2<=1.10 version yet

.. code-block:: python
    :linenos:

    settings = config.registry.settings
    config.include('pyramid_jinja2')

    from .models import (Model1, Model2, Model3,)
    # add sacrud and project models
    config.include('sacrud.pyramid_ext')
    settings['sacrud.models'] = {'Group1': {
                                    'tables': [Model1, Model2],
                                    'position': 1,},
                                 'Group2': {
                                    'tables': [Model3],
                                    'position': 4,}
                                }

check it there http://localhost:6543/sacrud/

Set another prefix
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    config.include('sacrud.pyramid_ext', route_prefix='admin')

now it there http://localhost:6543/admin/

Configure models
----------------

Model verbose name
~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:
    :emphasize-lines: 12

    class User(Base):

        __tablename__ = 'user'

        id = Column(Integer, primary_key=True)
        name = Column(String)

        def __init__(self, name):
            self.name = name

        # SACRUD
        verbose_name = 'My user model'

Instead "user", it will display "My user model"

.. image:: _static/img/verbose_name.png
    :alt: Model verbose name

Column verbose name
~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:
    :emphasize-lines: 7

    class User(Base):

        __tablename__ = 'user'

        id = Column(Integer, primary_key=True)
        name = Column(String,
                      info={"verbose_name": u'name of user', })

        def __init__(self, name):
            self.name = name

Instead "name", it will display "name of user"

.. image:: _static/img/column_verbose_name.png
    :alt: Column verbose name

Description for column
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:
    :emphasize-lines: 8

    class User(Base):

        __tablename__ = 'user'

        id = Column(Integer, primary_key=True)
        name = Column(String,
                      info={"verbose_name": u'name of user',
                            "description": "put there name"})

        def __init__(self, name):
            self.name = name

Adds a description below

.. image:: _static/img/column_description.png
    :alt: Column description

Add css class for column
~~~~~~~~~~~~~~~~~~~~~~~~

Configure the displayed fields in grid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure the displayed columns for detailed object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Composite fields and column as custom function
----------------------------------------------

Template redefinition
---------------------
