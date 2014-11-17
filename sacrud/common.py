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
import inspect
import itertools
import json
import os

import sqlalchemy


class TableProperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, inst, cls):
        return self.func(cls.__table__)


def get_attrname_by_colname(instance, name):
    """ Get value from SQLAlchemy instance by column name

    :Parameters:
        - `instance`: SQLAlchemy model instance.
        - `name`:  Column name

    :Examples:

    >>> from sqlalchemy import Column, Integer
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> Base = declarative_base()
    >>> class MPTTPages(Base):
    ...     __tablename__ = "mptt_pages"
    ...     id = Column(Integer, primary_key=True)
    ...     left = Column("lft", Integer, nullable=False)
    >>> get_attrname_by_colname(MPTTPages(), 'lft')
    'left'
    """
    for attr, column in list(sqlalchemy.inspect(instance.__class__).c.items()):
        if column.name == name:
            return attr


def get_relationship(table):
    if not table:
        return None
    relations = sqlalchemy.inspect(table).relationships
    return [rel for rel in relations]


def get_empty_instance(table):
    """ Return  empty instance of model.
    """
    instance_defaults_params = inspect.getargspec(table.__init__).args[1:]
    # list like ['name', 'group', 'visible'] to dict with empty
    # value as {'name': None, 'group': None, 'visible': None}
    init = dict(
        list(zip(instance_defaults_params, itertools.repeat(None)))
    )
    return table(**init)


def get_obj(session, table, pk):
    if not pk:
        return None
    pk_list = get_pk(table)
    obj = session.query(table)
    for item in pk_list:
        empty_obj = get_empty_instance(table)
        item_name = get_attrname_by_colname(empty_obj, item.name)
        obj = obj.filter(getattr(table, item_name) == pk[item_name])
    return obj.one()


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
    (Column('id', Integer(), table=<users>, primary_key=True, nullable=False),)
    >>> get_pk(User)
    (Column('id', Integer(), table=<users>, primary_key=True, nullable=False),)
    """
    if inspect.isclass(obj):
        pk_list = sqlalchemy.inspect(obj).primary_key
    else:
        pk_list = obj.__mapper__.primary_key
    return pk_list


def pk_to_list(obj, as_json=False):
    pk_list = []
    primary_keys = get_pk(obj)
    for item in primary_keys:
        item_name = get_attrname_by_colname(obj, item.name)
        pk_list.append(item_name)
        pk_list.append(getattr(obj, item_name))
    if as_json:
        return json.dumps(pk_list)
    return pk_list


def pk_list_to_dict(pk_list):
    """ convert list of multi pk to dict

    ['id', 1, 'id2', 22, 'foo', 'bar'] -> {'foo': 'bar', 'id2': 22, 'id': 1}
    """
    if pk_list and len(pk_list) % 2 == 0:
        return dict(zip(pk_list[::2], pk_list[1::2]))
    return None


def get_obj_by_request(session, table, request):
    pk = {}
    table_pk = get_pk(table)
    if not request:
        return None
    for item in table_pk:
        if item.name in request:
            pk[item.name] = request[item.name]
        else:
            return None
    try:
        return get_obj(session, table, pk)
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def delete_fileobj(table, obj, key):
    """ Delete atached file.
    """
    if hasattr(table, '__table__'):
        table = table.__table__
    abspath = table.columns[key].type.abspath
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
    obj = request[key]
    if isinstance(obj, (list, tuple)):
        obj = obj[0]
    filename = obj.filename

    # ``input_file`` contains the actual file data which needs to be
    # stored somewhere.

    input_file = obj.file

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
        try:
            output_file.write(bytearray(data, 'utf-8'))
        except UnicodeDecodeError:  # pragma: no cover
            output_file.write(bytearray(data))  # pragma: no cover
    output_file.close()


def columns_by_group(table):
    if 'sacrud_detail_col' in table.__dict__:
        return [c for c in table.sacrud_detail_col]
    return [('', table.__table__.columns)]


def get_flat_columns(table):
    columns = []
    if 'sacrud_detail_col' not in table.__dict__:
        return columns
    for item in table.sacrud_detail_col:
        for col in item[1]:
            columns.append(col)
    return columns
