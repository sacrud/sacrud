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

from sacrud.common.sa_helpers import (get_attrname_by_colname, get_pk,
                                      ObjPreprocessing, RequestPreprocessing,
                                      set_instance_name)

prefix = 'crud'


def get_empty_instance(table):
    """ Return  empty instance of model.
    """
    instance_defaults_params = inspect.getargspec(table.__init__).args[1:]
    # list like ['name', 'group', 'visible'] to dict with empty
    # value as {'name': None, 'group': None, 'visible': None}
    init = dict(
        zip(instance_defaults_params,
            itertools.repeat(None))
    )
    return table(**init)


def set_m2m_value(session, request, obj):
    """ Set m2m value for model obj from request params like "group[]"

        :Parameters:

            - `session`: SQLAlchemy DBSession
            - `request`: request as dict
            - `obj`: model instance
    """
    def get_m2m_objs(session, relation, ids):
        pk = relation.primary_key[0]
        return session.query(relation).filter(pk.in_(ids)).all()

    m2m_request = {k: v for k, v in request.items() if k[-2:] == '[]'}
    for k, v in m2m_request.iteritems():
        key = k[:-2]
        relation = getattr(obj.__class__, key, False)
        if not relation:
            continue  # pragma: no cover
        value = get_m2m_objs(session, relation.mapper, v)
        setattr(obj, key, value)
    return obj


class CRUD(object):
    """ Main class for CRUD actions

        :Parameters:

            - `session`: SQLAlchemy DBSession
            - `table`: SQLAlchemy model
            - `pk`: obj primary keys
            - `request`: web request
    """
    def __init__(self, session, table, pk=None, request=None):
        self.pk = get_pk(table)
        self.table = table
        self.request = request
        self.session = session
        self.obj = None
        if pk:
            obj = session.query(table)
            for item in self.pk:
                empty_obj = get_empty_instance(self.table)
                item_name = get_attrname_by_colname(empty_obj, item.name)
                obj = obj.filter(getattr(table, item_name) == pk[item_name])
            self.obj = obj.one()

    def rows_list(self):
        """
        Return a list of table rows.

        :Parameters:

            - `order_by`: name ordered row.
            - `paginator`: see sacrud.common.paginator.get_paginator.
        """
        table = self.table
        session = self.session
        col = [c for c in getattr(table, 'sacrud_list_col', table.__table__.columns)]
        row = session.query(table)

        if row.all():
            col = set_instance_name(row.all()[0], col)

        return {'row': row,
                'pk': self.pk,
                'col': col,
                'table': table,
                'prefix': prefix,
                }

    def add(self):
        """ Update row of table.

        :Example:

        .. code-block:: python

            resp = action.CRUD(dbsession, table, pk)
            resp.request = params
            resp.add()

        """
        columns = [c for c in self.table.__table__.columns]

        if self.request:
            # for create
            if not self.obj:
                self.obj = get_empty_instance(self.table)

            request_preprocessing = RequestPreprocessing(self.request)
            # filter request params for object
            for key, value in self.request.items():
                # chek if columns not exist
                if key not in self.table.__table__.columns:
                    if key[-2:] != '[]':
                        self.request.pop(key, None)
                    continue  # pragma: no cover
                self.request[key] = request_preprocessing.check_type(self.table, key)

            for key, value in self.request.iteritems():
                self.obj.__setattr__(key, value)

            # save m2m relationships
            self.obj = set_m2m_value(self.session, self.request, self.obj)

            self.session.add(self.obj)
            transaction.commit()
            return self.obj

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

        :Example:

        .. code-block:: python

            action.CRUD(dbsession, table, pk=pk).delete()
        """
        obj = ObjPreprocessing(obj=self.obj).delete()
        self.session.delete(obj)
        transaction.commit()
