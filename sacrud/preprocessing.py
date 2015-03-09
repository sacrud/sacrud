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
import inspect
import json
import uuid
from datetime import datetime, date

import six

from .common import delete_fileobj, store_file, get_columns


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
                           'FileStore': self._check_filestore,
                           'HSTORE': self._check_hstore,
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

    def _check_filestore(self, value):
        fileobj = value
        if hasattr(fileobj, 'filename'):
            extension = fileobj.filename.split(".")[-1]
            fileobj.filename = str(uuid.uuid4()) + "." + extension
            abspath = self.column.type.abspath
            store_file(self.request, self.key, abspath)
            value = fileobj.filename
        return value

    def _check_hstore(self, value):
        try:
            return ast.literal_eval(str(value))
        except Exception:
            raise TypeError("HSTORE: does't suppot '%s' format. %s" %
                            (value,
                             'Valid example: {"foo": "bar", u"baz": u"biz"}'))

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
        if type(value) in (list, tuple):
            value = value[0]

        if not value and not hasattr(value, 'filename'):
            if self.column.default or self.column.primary_key:
                return None

        if column_type in list(self.types_list.keys()):
            check = self.types_list[column_type]
            return check(value)

        return value


class ObjPreprocessing(object):

    def __init__(self, obj):
        self.obj = obj

    def add(self, session, request, table):
        request_preprocessing = RequestPreprocessing(request)
        # filter request for object
        for key in list(request.keys()):
            obj_columns = get_columns(self.obj)
            # check if columns not exist
            if key not in obj_columns and not hasattr(self.obj, key):
                if not key.endswith('[]'):
                    request.pop(key, None)
                continue  # pragma: no cover
            value = request_preprocessing.check_type(table, key)

            if value is None:
                request.pop(key, None)
                continue
            request[key] = value
        params = {k: v for k, v in request.items() if not k.endswith('[]')}
        m2m_params = get_m2m_value(session, request, self.obj)
        params = dict(list(params.items()) + list(m2m_params.items()))
        if inspect.isclass(self.obj):
            return self.obj(**params)
        for k, v in params.items():
            setattr(self.obj, k, v)
        return self.obj

    def delete(self):
        obj_columns = get_columns(self.obj)
        for col in obj_columns:
            if col.type.__class__.__name__ == 'FileStore':
                if not getattr(self.obj, col.name):
                    continue  # pragma: no cover
                delete_fileobj(self.obj.__table__, self.obj, col.name)
        return self.obj
