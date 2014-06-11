#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Views for Pyramid frontend
"""
import itertools
import json
from collections import OrderedDict

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
from sqlalchemy import inspect

from sacrud import action
from sacrud.common.paginator import get_paginator
from sacrud.common.pyramid_helpers import get_settings_param, sacrud_env
from sacrud.common.sa_helpers import pk_to_list
from sacrud.pyramid_ext.breadcrumbs import breadcrumbs


def get_table(tname, request):
    """ Return table by table name from sacrud.models in settings.
    """
    # convert values of models dict to flat list
    setting_params = get_settings_param(request, 'sacrud.models').values()
    tables_lists = map(lambda x: x['tables'], setting_params)
    tables = itertools.chain(*tables_lists)
    tables = filter(lambda table: (table.__tablename__).
                    lower() == tname.lower(), tables)
    if not tables:
        return None
    return tables[0]


def get_relationship(tname, request):
    table = get_table(tname, request)
    if not table:
        return None
    relations = inspect(table).relationships
    return [rel for rel in relations]


def update_difference_object(obj, key, value):
    if isinstance(obj, dict):
        obj.update({key: value})
    else:
        setattr(obj, key, value)
    # return obj


def pk_list_to_dict(pk_list):
    if pk_list and len(pk_list) % 2 == 0:
        return dict(zip(pk_list[::2], pk_list[1::2]))
    return None


@view_config(route_name='sa_save_position', request_method='POST',
             renderer='json')
def sa_save_position(request):
    """ col1 col2 col3
         w1   w2   w3
         w4   w5   w6
         w7   w8   w9

         Example w4 move to col3 after w3:
             w6 and w9 position = position + 3
             w4 = 2*3 - 3 + 3 = 6

         Example w4 move to col2 after w2:
             w5 and w8 position = position + 3
             w4 = 2*3 - 3 + 2 = 5

         Example w5 move to col1 after w4:
             w7 position = position + 3
             w5 = 3*3 - 3 + 1 = 7
    """
    kwargs = dict(request.POST)
    session = request.dbsession
    columns = request.registry.settings\
        .get('sacrud_dashboard_columns', 3)
    PositionModel = request.registry.settings\
        .get('sacrud_dashboard_position_model', None)
    if not PositionModel:
        return
    position = (int(kwargs['position']) + 1) * columns - columns + int(kwargs['column'])
    session.query(PositionModel)\
        .filter(PositionModel.position % columns == position % columns)\
        .filter(PositionModel.position >= position)\
        .update({'position': PositionModel.position + columns})
    widget = session.query(PositionModel)\
        .filter_by(widget=kwargs['widget'] or None).one()
    widget.position = position
    return {'result': 'ok'}


def sorted_dashboard_widget(tables, dashboard_columns=3, session=None,
                            model=None):
    def get_position(name):
        if model and session:
            return session.query(model).filter_by(widget=(name or None)).one().position
        return tables[name]['position']

    def set_position(name, value):
        value['position'] = get_position(name)
        return value

    def getKey(item):
        position = item[1]['position']
        key = position % dashboard_columns
        if not key:
            key = dashboard_columns
        return (key, position)

    dashboard_widget = {k: set_position(k, v) for k, v in tables.iteritems()}
    return OrderedDict(sorted(dashboard_widget.iteritems(),
                              cmp=lambda t1, t2: cmp(getKey(t1), getKey(t2))))


@view_config(route_name='sa_home', renderer='/sacrud/home.jinja2')
def sa_home(request):
    session = request.dbsession
    tables = get_settings_param(request, 'sacrud.models')
    dashboard_columns = request.registry.settings\
        .get('sacrud_dashboard_columns', 3)
    dashboard_model = request.registry.settings.get('sacrud_dashboard_position_model', None)
    return {'dashboard_columns': dashboard_columns,
            'tables': sorted_dashboard_widget(tables, dashboard_columns,
                                              session, dashboard_model)
            }


class CRUD(object):

    def __init__(self, request):
        self.pk = None
        self.request = request
        self.tname = request.matchdict['table']
        self.table = get_table(self.tname, self.request)
        self.relationships = get_relationship(self.tname, self.request)
        self.params = request.params.dict_of_lists()

        pk = request.matchdict.get('pk')
        if pk and len(pk) % 2 == 0:
            self.pk = pk_list_to_dict(pk)
        elif pk or pk == ():
            raise HTTPNotFound

    def flash_message(self, message, status="success"):
        if hasattr(self.request, 'session'):
            self.request.session.flash([message, status])

    # XXX: C901
    @sacrud_env
    @view_config(route_name='sa_list', renderer='/sacrud/list.jinja2')
    def sa_list(self):
        table = self.table
        request = self.request
        order_by = request.params.get('order_by', False)
        search = request.params.get('search')
        get_params = {'order_by': order_by, 'search': search}

        # Make url for table headrow links to order_by
        for col in getattr(table, 'sacrud_list_col', table.__table__.columns):
            order_param_list = []
            column_name = col['column'].name if isinstance(col, dict) else col.name
            if order_by:
                if column_name not in order_by.replace('-', '').split('.'):
                    order_param_list.append(column_name)

                for value in order_by.split('.'):
                    none, pfx, col_name = value.rpartition('-')
                    if column_name == col_name:
                        new_pfx = {'': '-', '-': ''}[pfx]
                        order_param_list.insert(0, '%s%s' % (new_pfx, col_name))
                    else:
                        order_param_list.append('%s%s' % (pfx, col_name))
            else:
                order_param_list.append(column_name)

            full_params = ['%s=%s' % (param, value) for param, value in get_params.items()
                           if param != 'order_by' and value]
            full_params.append('order_by=%s' % '.'.join(order_param_list))
            update_difference_object(col, 'head_url', '&'.join(full_params))

        # Some actions with objects in grid
        selected_action = request.POST.get('selected_action')
        items_list = request.POST.getall('selected_item')
        if selected_action == 'delete':
            for item in items_list:
                pk_list = json.loads(item)
                pk = pk_list_to_dict(pk_list)
                action.CRUD(request.dbsession, table, pk=pk).delete()

        items_per_page = getattr(table, 'items_per_page', 10)
        resp = action.CRUD(request.dbsession, table)\
            .rows_list(paginator=get_paginator(request, items_per_page),
                       order_by=order_by, search=search)

        return {'sa_crud': resp,
                'pk_to_list': pk_to_list,
                'breadcrumbs': breadcrumbs(self.tname, 'sa_list'),
                'get_params': get_params}

    @sacrud_env
    @view_config(route_name='sa_update', renderer='/sacrud/create.jinja2')
    @view_config(route_name='sa_create', renderer='/sacrud/create.jinja2')
    def sa_add(self):
        resp = action.CRUD(self.request.dbsession, self.table, self.pk)

        if 'form.submitted' in self.request.params:
            resp.request = self.params
            resp.add()
            if self.pk:
                self.flash_message("You updated object of %s" % self.tname)
            else:
                self.flash_message("You created new object of %s" % self.tname)
            return HTTPFound(location=self.request.route_url('sa_list',
                                                             table=self.tname))

        bc = breadcrumbs(self.tname, 'sa_create')
        if self.pk:
            bc = breadcrumbs(self.tname, 'sa_update', id=self.pk)

        return {'sa_crud': resp.add(),
                'pk_to_list': pk_to_list,
                'relationships': self.relationships,
                'breadcrumbs': bc}

    @view_config(route_name='sa_delete')
    def sa_delete(self):
        action.CRUD(self.request.dbsession, self.table, pk=self.pk).delete()
        self.flash_message("You have removed object of %s" % self.tname)
        return HTTPFound(location=self.request.route_url('sa_list',
                                                         table=self.tname))
