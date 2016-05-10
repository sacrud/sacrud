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
import json
import inspect
import itertools

import sqlalchemy
from sqlalchemy import or_, and_


def unjson(obj):
    try:
        return json.loads(obj)
    except TypeError:
        pass
    return obj


class TableProperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, inst, cls):
        return self.func(cls.__table__)


class ClassProperty(TableProperty):
    def __get__(self, inst, cls):
        return self.func(cls)


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

    def composite_pk_clauses(pk):
        clauses = []
        for item in pk_list:
            clauses.append(getattr(table, item.name) == pk[item.name])
        return and_(*clauses)

    query = session.query(table)
    if type(pk) is list or type(pk) is tuple:
        if all(type(item) is dict for item in pk):
            clauses = []
            for item in pk:
                clauses.append(composite_pk_clauses(item))
            return query.filter(or_(*clauses))
        return query.filter(pk_list[0].in_(pk))
    elif (type(pk) is int or str(pk).isdigit()) and len(pk_list) == 1:
        return query.get(pk)
    elif type(pk) is dict:
        return query.filter(composite_pk_clauses(pk))
    return None  # pragma: no cover


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


def pk_to_dict(obj):
    pk_list = pk_to_list(obj)
    return pk_list_to_dict(pk_list)


def pk_list_to_dict(pk_list):
    """ convert list of multi pk to dict

    ['id', 1, 'id2', 22, 'foo', 'bar'] -> {'foo': 'bar', 'id2': 22, 'id': 1}
    """
    if pk_list and len(pk_list) % 2 == 0:
        return dict(zip(pk_list[::2], pk_list[1::2]))
    return None


def get_obj_by_request_data(session, table, data):
    pk = {}
    table_pk = get_pk(table)
    if not data:
        return None
    for item in table_pk:
        if item.name in data:
            pk[item.name] = data[item.name]
        else:
            return None
    try:
        return get_obj(session, table, pk)
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def columns_by_group(table):
    if hasattr(table, 'sacrud_detail_col'):
        return [c for c in table.sacrud_detail_col]
    # https://groups.google.com/forum/#!msg/sqlalchemy/k0MrlMBvAls/XPJqKzMYFQAJ
    return [
        ('',
         [
             (c.key, c._orig_columns[0])
             for c in sorted(
                     sqlalchemy.inspection.inspect(table).column_attrs,
                     key=lambda col: col.columns[0]._creation_order)
         ])
    ]


def get_flat_columns(table):
    columns = []
    if not hasattr(table, 'sacrud_detail_col'):
        return columns
    for item in table.sacrud_detail_col:
        for col in item[1]:
            columns.append(col)
    return columns


def get_columns(obj):
    if hasattr(obj, '__table__'):
        return obj.__table__.columns
    return sqlalchemy.inspect(obj).mapper.columns
