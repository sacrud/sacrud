CRUD interface for SQLAlchemy with Pyramid gateway.
DOCS WITH NEXT RELEASE!

INSTALL
===

PyPi
---
pip install sacrud

Source
---
python setup.py install

USAGE
=====

Add to your project config:

    # pyramid_jinja2 configuration
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("myprojectname:templates")

    from .models import (Model1, Model2, Model3,)
    # add sacrud and project models
    config.include('sacrud.pyramid_ext')
    settings = config.registry.settings
    settings['sacrud_models'] = (Model1, Model2, Model3)

go to http://localhost:6543/sacrud 

SCREENSHOTS
===========
list of tables
--------------
![ScreenShot](https://raw.github.com/uralbash/sacrud/master/sacrud/doc/tables.png)

list of rows
--------------
![ScreenShot](https://raw.github.com/uralbash/sacrud/master/sacrud/doc/row_list.png)

edit row
--------------
![ScreenShot](https://raw.github.com/uralbash/sacrud/master/sacrud/doc/edit.png)
