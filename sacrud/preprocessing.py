#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Preprocessing
"""
import ast
import json
import inspect
from datetime import date, datetime

import six

import sqlalchemy

from .common import get_columns


def list_of_lists_to_dict(l):
    """ Convert list of key,value lists to dict

    [['id', 1], ['id', 2], ['id', 3], ['foo': 4]]
    {'id': [1, 2, 3], 'foo': [4]}
    """
    d = {}
    for key, val in l:
        d.setdefault(key, []).append(val)
    return d


def get_m2m_objs(session, relation, id_from_request):
    mapper = relation.mapper
    pk_list = mapper.primary_key
    ids = []
    if id_from_request:
        if isinstance(id_from_request, six.string_types):
            id_from_request = [id_from_request, ]
        for id in id_from_request:
            try:
                ids.append(json.loads(id))
            except ValueError:
                pass
            except TypeError:
                return None
        ids = list_of_lists_to_dict(ids)
    else:
        ids = {}
    objs = session.query(mapper)
    for pk in pk_list:
        objs = objs.filter(pk.in_(ids.get(pk.name, [])))
    return objs.all()


def get_m2m_value(session, request, obj):
    """ Set m2m value for model obj from request params like "group[]"

        :Parameters:

            - `session`: SQLAlchemy DBSession
            - `request`: request as dict
            - `obj`: model instance
    """
    params = {}
    ''' m2m_request:

        {u'company[]': [u'["id", 1]'],
         u'professions[]': [u'["id", 2]', u'["id", 3]']}
    '''
    m2m_request = {k: v for k, v in list(request.items()) if k.endswith('[]')}
    for k, v in list(m2m_request.items()):
        key = k[:-2]
        relation = getattr(obj.__class__, key, False)
        if not relation:
            relation = getattr(obj, key, False)
        if not relation:
            continue  # pragma: no cover
        value = get_m2m_objs(session, relation, v)
        if value is None:
            continue

        if relation.property.uselist is False:
            if value:
                value = value[0]
            else:
                value = None
        params[key] = value
    return params


class RequestPreprocessing(object):

    def __init__(self, request):
        self.request = request
        self.types_list = {'Boolean': self._check_boolean,
                           'HSTORE': self._check_hstore,
                           'JSON': self._check_hstore,
                           'JSONB': self._check_hstore,
                           'Date': self._check_date,
                           'DateTime': self._check_date,
                           'BYTEA': self._check_bytea,
                           'LargeBinary': self._check_bytea,
                           'TIMESTAMP': self._check_date
                           }

    def _check_boolean(self, value):
        if not value:
            return False
        if value in ('0', 'False', 'None', 'false'):
            return False
        return True

    def _check_bytea(self, value):
        return bytearray(value, 'utf-8')

    def _check_hstore(self, value):
        if not value:
            return None
        try:
            return json.loads(str(value))
        except Exception:
            try:
                return ast.literal_eval(str(value))
            except Exception:
                raise TypeError(
                    "[HSTORE, JSON, JSONB]: does't suppot '%s' format. %s" %
                    (value, 'Valid example: {"foo": "bar", u"baz": u"biz"}'))

    def _check_date(self, value):
        if isinstance(value, (date, datetime)):
            return value
        # XXX: I feel the dissonance here
        try:
            return datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(value, '%Y-%m-%d %H:%M')
            except ValueError:
                return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    def check_type(self, table, key):
        self.key = key
        self.column = None
        obj_columns = get_columns(table)
        if key in obj_columns:
            self.column = obj_columns[key]
        else:
            self.column = getattr(table, key)
        column_type = self.column.type.__class__.__name__
        value = self.request[key]
        if type(value) in (list, tuple) and\
                column_type not in ['JSON', 'JSONB', 'HSTORE']:
            value = value[0]

        if not isinstance(value, sqlalchemy.sql.elements.Null) and not value\
                and not hasattr(value, 'filename')\
                and not column_type == 'Boolean':
            if self.column.default or self.column.primary_key:
                return None

        if column_type in list(self.types_list.keys()):
            check = self.types_list[column_type]
            return check(value)

        return value


class ObjPreprocessing(object):

    def __init__(self, obj):
        self.obj = obj

    def add(self, session, data, table):
        request_preprocessing = RequestPreprocessing(data)
        # filter data for object
        for key in list(data.keys()):
            obj_columns = get_columns(self.obj)
            # check if columns not exist
            if key not in obj_columns and not hasattr(self.obj, key):
                if not key.endswith('[]'):
                    data.pop(key, None)
                continue  # pragma: no cover
            value = request_preprocessing.check_type(table, key)

            if value is None:
                data.pop(key, None)
                continue
            data[key] = value
        params = {k: v for k, v in data.items() if not k.endswith('[]')}
        m2m_params = get_m2m_value(session, data, self.obj)
        params = dict(list(params.items()) + list(m2m_params.items()))
        if inspect.isclass(self.obj):
            return self.obj(**params)
        for k, v in params.items():
            setattr(self.obj, k, v)
        return self.obj

    def delete(self):
        return self.obj
