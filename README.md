sacrud
======

sacrud will solve your problem of CRUD interface for SQLAlchemy,
by providing extension for Pyramid or use it in pure form.

Look how easy it is to use with Pyramid:

    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("myprojectname:templates")

    from .models import (Model1, Model2, Model3,)
    # add sacrud and project models
    config.include('sacrud.pyramid_ext')
    settings = config.registry.settings
    settings['sacrud_models'] = (Model1, Model2, Model3)

go to http://localhost:6543/sacrud/

and see...
![ScreenShot](https://raw.github.com/uralbash/sacrud/master/docs/img/index.png)

Features
--------

- Be awesome
- Read table rows
![ScreenShot](https://raw.github.com/uralbash/sacrud/master/docs/img/rows.png)
- Create and update row
![ScreenShot](https://raw.github.com/uralbash/sacrud/master/docs/img/edit.png)
- Delete row
- Use sortable table with poition field
- Upload file with FileField
- Union row (testing)
- Custom style

Installation
------------

Install from github:

    pip install git+http://github.com/uralbash/sacrud.git

PyPi:

    pip install sacrud

Source:

    python setup.py install

Contribute
----------

- Issue Tracker: github.com/uralbash/sacrud/issues
- Source Code: github.com/uralbash/sacrud
- Docs: sacrud.readthedocs.org (in process)

Support
-------

If you are having issues, please let me know.
I have a mailing list located at: sacrud@uralbash.ru

License
-------

The project is licensed under the BSD license.

Example
-------
![ScreenShot](https://raw.github.com/uralbash/sacrud/master/docs/img/example.png)
