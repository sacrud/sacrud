#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
CREATE, READ, DELETE, UPDATE actions for SQLAlchemy models
"""
import inspect
import transaction

from webhelpers.paginate import Page
from sacrud.common.sa_helpers import (
    check_type,
    get_pk,
    get_relations,
)

prefix = 'crud'


def list(session, table, paginator=None, order_by=None):
    """
    Return a list of table rows.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `order_by`: name ordered row.
        - `paginator`: see sacrud.common.paginator.get_paginator.
    """
    col = [c for c in getattr(table, 'sacrud_list_col', table.__table__.columns)]
    pk_name = get_pk(table)
    query = session.query(table)
    if order_by:
        query = query.order_by(order_by)
    row = query.all()
    if paginator:
        row = Page(row, **paginator)
    if hasattr(table, '__mapper_args__'):
        mapper_args = table.__mapper_args__
    else:
        mapper_args = {}

    return {'row': row,
            'pk': pk_name,
            'col': col,
            'table': table,
            'prefix': prefix,
            'mapper_args': mapper_args, }


def create(session, table, request=''):
    """
    Insert row to table.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `request`: webob format request.
    """
    if request:
        args = {}
        # FIXME: я чувствую здесь диссонанс
        for arg in inspect.getargspec(table.__init__).args[1:]:
            args[arg] = None
        obj = table(**args)
        for key, value in request.items():
            # chek columns exist
            if not key in table.__table__.columns:
                continue
            value = check_type(request, table, key)
            obj.__setattr__(key, value)
        session.add(obj)
        transaction.commit()
        return

    pk_name = get_pk(table)
    col = [c for c in getattr(table, 'sacrud_detail_col', table.__table__.columns)]
    return {'pk': pk_name,
            'col': col,
            'table': table,
            'prefix': prefix}


def read(session, table, pk):
    """
    Select row by pk.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `pk`: primary key value.
    """
    pk_name = get_pk(table)
    obj = session.query(table).filter(getattr(table, pk_name) == pk).one()
    col = [c for c in getattr(table, 'sacrud_list_col', table.__table__.columns)]
    return {'obj': obj,
            'pk': pk_name,
            'col': col,
            'table': table,
            'prefix': prefix,
            'rel': get_relations(obj)}


def update(session, table, pk, request=''):
    """
    Update row of table.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `request`: webob format request.
    """

    pk_name = get_pk(table)
    obj = session.query(table).filter(getattr(table, pk_name) == pk).one()
    col_list = [c for c in table.__table__.columns]

    if request:
        for col in col_list:
            if col.name not in request:
                continue
            if getattr(obj, col.name) == request[col.name][0]:
                continue
            if col.type.__class__.__name__ == 'FileStore':
                if not hasattr(request[col.name][0], 'filename'):
                    continue
            value = check_type(request, table, col.name, obj)
            setattr(obj, col.name, value)
        session.add(obj)
        transaction.commit()
        return
    col_list = [c for c in getattr(table, 'sacrud_detail_col', table.__table__.columns)]
    return {'obj': obj,
            'pk': pk_name,
            'col': col_list,
            'table': table,
            'prefix': prefix}


def delete(session, table, pk):
    """
    Delete row by pk.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `pk`: primary key value.
    """

    pk_name = get_pk(table)
    obj = session.query(table).filter(getattr(table, pk_name) == pk).one()
    check_type('', table, obj=obj)
    session.delete(obj)
    transaction.commit()
