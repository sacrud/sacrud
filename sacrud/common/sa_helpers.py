#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
SQLAlchemy helpers
"""
import os
import ast
import uuid
import inspect
import sqlalchemy


def get_pk(obj):
    """ Return primary key name by model class or instance.

    :Parameters:
        - `obj`: SQLAlchemy model instance or class.

    :Examples:

    >>> from sqlalchemy import Column, Integer
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> Base = declarative_base()
    >>> class User(Base):
    ...     __tablename__ = 'users'
    ...     id = Column(Integer, primary_key=True)
    >>> get_pk(User())
    'id'
    >>> get_pk(User)
    'id'

    """
    if inspect.isclass(obj):
        pk_list = sqlalchemy.inspect(obj).primary_key
    else:
        pk_list = obj.__mapper__.primary_key
    if pk_list:
        return pk_list[0].name

    return ''


def get_relations(obj):
    """
    :Examples:

    >>> from sqlalchemy import Column, Integer, ForeignKey
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> from sqlalchemy.orm import relationship, backref
    >>> Base = declarative_base()
    >>> class User(Base):
    ...    __tablename__ = 'users'
    ...    id = Column(Integer, primary_key=True)
    ...
    >>> class Address(Base):
    ...    __tablename__ = 'addresses'
    ...    id = Column(Integer, primary_key=True)
    ...    user_id = Column(Integer, ForeignKey('users.id'))
    ...    user = relationship("User", backref=backref('addresses', order_by=id))
    >>> get_relations(User())
    [('addresses', [])]

    """
    return [(n, getattr(obj, n)) for n in dir(obj)
            if isinstance(getattr(obj, n),
                          sqlalchemy.orm.collections.InstrumentedList)]


def delete_fileobj(table, obj, key):
    """ Delete atached file.
    """
    abspath = table.__table__.columns[key].type.abspath
    path = os.path.join(abspath, os.path.basename(getattr(obj, key)))
    if not obj or not os.path.isfile(path):
        return
    os.remove(path)


def store_file(request, key, path):
    """ Load atached file.
    """
    # ``filename`` contains the name of the file in string format.
    #
    # WARNING: this example does not deal with the fact that IE sends an
    # absolute file *path* as the filename.  This example is naive; it
    # trusts user input.
    filename = request[key][0].filename

    # ``input_file`` contains the actual file data which needs to be
    # stored somewhere.

    input_file = request[key][0].file

    # Using the filename like this without cleaning it is very
    # insecure so please keep that in mind when writing your own
    # file handlingself.
    file_path = os.path.join(path, filename)
    output_file = open(file_path, 'wb')

    # Finally write the data to the output file
    input_file.seek(0)
    while 1:
        data = input_file.read(2 << 16)
        if not data:
            break
        output_file.write(data)
    output_file.close()


def check_type(request, table, key=None, obj=None):
    """ Chek type when Create, Update or Delete.
    """
    # XXX: C901 very ugly function
    # for Delete
    if not key:
        for col in table.__table__.columns:
            if col.type.__class__.__name__ == 'FileStore':
                if getattr(obj, col.name):
                    delete_fileobj(table, obj, col.name)
        return
    column = table.__table__.columns[key]
    column_type = column.type.__class__.__name__

    # for Update or Create
    value = request[key]
    if type(value) in (list, tuple):
        value = value[0]

    if not value and not hasattr(value, 'filename'):
        return None

    if column_type == 'Boolean':
        value = False if value == '0' else True
        value = True if value else False
    elif column_type == 'FileStore':
        fileobj = value
        if hasattr(fileobj, 'filename'):
            extension = fileobj.filename.split(".")[-1]
            fileobj.filename = str(uuid.uuid4()) + "." + extension
            abspath = table.__table__.columns[key].type.abspath
            store_file(request, key, abspath)
            if obj:
                if getattr(obj, key):
                    delete_fileobj(table, obj, key)
            value = fileobj.filename
    elif column_type == 'HSTORE':
        try:
            value = ast.literal_eval(value)
        except:
            raise TypeError("HSTORE: does't suppot '%s' format. %s" %
                            (value, 'Valid example: {"foo": "bar", u"baz": u"biz"}'))
    elif column_type == 'Date':
        from datetime import datetime
        value = datetime.strptime(value, '%Y-%m-%d')
    return value
