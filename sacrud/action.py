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
import itertools

import transaction
from sqlalchemy import desc, or_
from webhelpers.paginate import Page

from sacrud.common.sa_helpers import check_type, get_pk, set_instance_name

prefix = 'crud'


def get_empty_instance(table):
    instance_defaults_params = inspect.getargspec(table.__init__).args[1:]
    # list like ['name', 'group', 'visible'] to dict with empty
    # value as {'name': None, 'group': None, 'visible': None}
    init = dict(
        zip(instance_defaults_params,
            itertools.repeat(None))
    )
    return table(**init)


def get_m2m_objs(session, relation, ids):
    pk = relation.primary_key[0]
    return session.query(relation).filter(pk.in_(ids)).all()


def set_m2m_value(session, request, obj):
    m2m_request = {k: v for k, v in request.items() if k[-2:] == '[]'}
    for k, v in m2m_request.iteritems():
        key = k[:-2]
        relation = getattr(obj.__class__, key)
        value = get_m2m_objs(session, relation.mapper, v)
        setattr(obj, key, value)
    return obj


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

    def rows_list(self, paginator=None, order_by=None, search=None):
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
        if search:
            search_filter_group = [search_col.like('%%%s%%' % search)
                                   for search_col in getattr(table, 'sacrud_search_col', [])]
            query = query.filter(or_(*search_filter_group))

        if order_by:
            order_filter_group = []
            for value in order_by.split('.'):
                none, pfx, col_name = value.rpartition('-')
                order_filter_group.append(desc(col_name) if pfx == '-' else col_name)
            query = query.order_by(*order_filter_group)
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

    def add(self):
        """ Update row of table.
        """
        columns = [c for c in self.table.__table__.columns]

        if self.request:
            # for create
            if not self.obj:
                self.obj = get_empty_instance(self.table)

            # save m2m relationships
            self.obj = set_m2m_value(self.session, self.request, self.obj)

            # filter request params for object
            for key, value in self.request.items():
                # chek if columns not exist
                if key not in self.table.__table__.columns:
                    self.request.pop(key, None)
                    continue
                self.request[key] = check_type(self.request, self.table, key)

            for key, value in self.request.iteritems():
                self.obj.__setattr__(key, value)

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

    def delete(self):
        """ Delete row by pk.
        """
        # check_type('', table, obj=obj)
        self.session.delete(self.obj)
        transaction.commit()
