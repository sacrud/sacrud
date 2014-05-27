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
from sqlalchemy.orm.exc import NoResultFound
from webhelpers.paginate import Page

from sacrud.common.sa_helpers import check_type, get_pk, set_instance_name

prefix = 'crud'

# FIXME: rewrite it
get_pk_hook = lambda x: get_pk(x)[0].name


def get_m2m_objs(session, relation, ids):
    pk = relation.primary_key[0]
    return session.query(relation).filter(pk.in_(ids)).all()


def set_m2m_value(session, request, obj):
    m2m_request = {k: v for k, v in request.iteritems() if k[-2:] == '[]'}
    for k, v in m2m_request.iteritems():
        key = k[:-2]
        relation = getattr(obj.__class__, key)
        value = get_m2m_objs(session, relation.mapper, v)
        setattr(obj, key, value)


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
            if key not in table.__table__.columns:
                continue
            value = check_type(request, table, key)
            obj.__setattr__(key, value)

        # save m2m relationships
        set_m2m_value(session, request, obj)
        session.add(obj)
        transaction.commit()
        return

    pk_name = get_pk_hook(table)
    col = [c for c in getattr(table, 'sacrud_detail_col', [('', table.__table__.columns)])]
    return {'pk': pk_name,
            'col': col,
            'table': table,
            'prefix': prefix}


class CRUD(object):
    def __init__(self, session, table, pk=None, request=None):
        self.pk = get_pk(table)
        self.table = table
        self.request = request
        self.session = session
        self.obj = None
        if pk:
            obj = session.query(table)
            for item in self.pk:
                obj = obj.filter(getattr(table, item.name) == pk[item.name])
            self.obj = obj.one()

    def rows_list(self, paginator=None, order_by=None):
        """
        Return a list of table rows.

        :Parameters:

            - `order_by`: name ordered row.
            - `paginator`: see sacrud.common.paginator.get_paginator.
        """
        table = self.table
        session = self.session
        col = [c for c in getattr(table, 'sacrud_list_col', table.__table__.columns)]
        query = session.query(table)
        if order_by:
            query = query.order_by(order_by)
        row = query.all()
        if paginator:
            row = Page(row, **paginator)
        if row:
            col = set_instance_name(row[0], col)

        return {'row': row,
                'pk': self.pk,
                'col': col,
                'table': table,
                'prefix': prefix,
                }

    def read(self):
        """ Select row by pk.
        """
        columns = [c for c in getattr(self.table, 'sacrud_list_col', self.table.__table__.columns)]
        return {'obj': self.obj,
                'pk': self.pk,
                'col': columns,
                'table': self.table,
                'prefix': prefix}

    def update(self):
        """ Update row of table.
        """
        columns = [c for c in self.table.__table__.columns]
        set_instance_name(self.obj, columns)

        if self.request:
            for col in columns:
                if col.name not in self.request:
                    continue
                if getattr(self.obj, col.instance_name,
                           col.name) == self.request[col.name][0]:
                    continue
                # XXX: not good
                if col.type.__class__.__name__ == 'FileStore':
                    if not hasattr(self.request[col.name][0], 'filename'):
                        continue
                value = check_type(self.request, self.table,
                                   col.name, self.obj)
                setattr(self.obj, col.name, value)

            # save m2m relationships
            set_m2m_value(self.session, self.request, self.obj)
            self.session.add(self.obj)
            transaction.commit()
            return

        columns = [c for c in getattr(self.table,
                                      'sacrud_detail_col',
                                      [('', self.table.__table__.columns)])]
        return {'obj': self.obj,
                'pk': self.pk,
                'col': columns,
                'table': self.table,
                'prefix': prefix}


def delete(session, table, pk):
    """
    Delete row by pk.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `pk`: primary key value.
    """

    pk_name = get_pk_hook(table)
    try:
        if not isinstance(pk, list):
            pk = [pk]
        query_obj = session.query(table).filter(getattr(table, pk_name).in_(pk))
        for obj in query_obj.all():
            check_type('', table, obj=obj)
        query_obj.delete(synchronize_session=False)
        transaction.commit()
    except NoResultFound:
        pass
