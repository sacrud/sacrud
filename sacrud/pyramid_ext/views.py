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
import operator

import transaction
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
from sqlalchemy import inspect

from sacrud import action
from sacrud.common.paginator import get_paginator
from sacrud.common.pyramid_helpers import get_settings_param
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


@view_config(route_name='sa_save_position', request_method='POST',
             renderer='json')
def sa_save_position(request):
    kwargs = dict(request.POST)
    session = request.dbsession
    PositionModel = request.sacrud_dashboard_position_model

    if PositionModel:
        widget_obj = session.query(PositionModel).filter(PositionModel.widget == kwargs['widget']).first()
        old_column = getattr(widget_obj, 'column', 0)
        old_position = getattr(widget_obj, 'position', 0)

        if widget_obj:
            # setattr(widget_obj, 'column', kwargs['column'])
            widget_obj.column = int(kwargs['column'])
            widget_obj.position = int(kwargs['position'])
        else:
            widget_obj = PositionModel(**kwargs)
        session.add(widget_obj)

        if old_column == widget_obj.column:
            if old_position < widget_obj.position:
                session.query(PositionModel)\
                    .filter(PositionModel.id != widget_obj.id,
                            PositionModel.column == kwargs['column'],
                            PositionModel.position <= kwargs['position'],
                            PositionModel.position > old_position)\
                    .update({'position': PositionModel.position-1})
            else:
                session.query(PositionModel)\
                    .filter(PositionModel.id != widget_obj.id,
                            PositionModel.column == kwargs['column'],
                            PositionModel.position >= kwargs['position'],
                            PositionModel.position < old_position)\
                    .update({'position': PositionModel.position+1})
        else:
            old_neighbors = session.query(PositionModel)\
                                   .filter(PositionModel.column == old_column)\
                                   .all()
            for i, old_neighbor in enumerate(old_neighbors):
                old_neighbor.position = i

            session.query(PositionModel)\
                   .filter(PositionModel.id != widget_obj.id,
                           PositionModel.column == kwargs['column'],
                           PositionModel.position >= kwargs['position'])\
                   .update({'position': PositionModel.position+1})

        transaction.commit()
    return {'result': 'ok'}


class WidgetPositionObject(object):
    def __init__(self, title, tables):
        self.title = title
        self.tables = tables


@view_config(route_name='sa_home', renderer='/sacrud/home.jinja2')
def sa_home(request):
    # XXX: C901
    tables = get_settings_param(request, 'sacrud.models')
    sacrud_dashboard_columns = request.registry.settings\
                                      .get('sacrud_dashboard_columns', 3)
    context = {'dashboard_columns': sacrud_dashboard_columns}
    PositionModel = request.sacrud_dashboard_position_model
    items_list = {}
    if PositionModel:
        for column in range(sacrud_dashboard_columns):
            widgets = request.dbsession.query(PositionModel.widget)\
                                       .filter(PositionModel.column == column,
                                               PositionModel.widget.in_(tables.keys()))\
                                       .order_by(PositionModel.column,
                                                 PositionModel.position)\
                                       .all()
            # widgets = [w[0] for w in widgets]
            items_list.update({column: [], })
            for widget_item in widgets:
                if widget_item[0] in tables.keys():
                    items_list[column].append(
                        WidgetPositionObject(widget_item[0],
                                             tables[widget_item[0]]['tables'])
                    )
    else:
        for column in range(sacrud_dashboard_columns):
            items_list.update({column: [], })
            for group, table_obj in sorted(tables.iteritems(), key=operator.itemgetter(1)):
                if 'column' not in table_obj:
                    table_obj['column'] = 0
                    items_list[0].append(WidgetPositionObject(group, table_obj['tables']))
                elif table_obj['column'] == column:
                    items_list[column].append(WidgetPositionObject(group, table_obj['tables']))

    context.update({'tables': items_list})
    return context


def update_difference_object(obj, key, value):
    if isinstance(obj, dict):
        obj.update({key: value})
    else:
        setattr(obj, key, value)
    # return obj


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
            self.pk = dict(zip(pk[::2], pk[1::2]))
        elif pk or pk == ():
            raise HTTPNotFound

    def flash_message(self, message, status="success"):
        if hasattr(self.request, 'session'):
            self.request.session.flash([message, status])

    # XXX: C901
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
                # FIXME: add Multi-Column pk
                action.CRUD(request.dbsession, table, pk={'id': item}).delete()

        items_per_page = getattr(table, 'items_per_page', 10)
        resp = action.CRUD(request.dbsession, table)\
            .rows_list(paginator=get_paginator(request, items_per_page),
                       order_by=order_by, search=search)

        return {'sa_crud': resp,
                'pk_to_list': pk_to_list,
                'breadcrumbs': breadcrumbs(self.tname, 'sa_list'),
                'get_params': get_params}

    @view_config(route_name='sa_create', renderer='/sacrud/create.jinja2')
    def sa_create(self):
        if 'form.submitted' in self.request.params:
            action.create(self.request.dbsession, self.table,
                          self.request.params.dict_of_lists())
            self.flash_message("You created new object of %s" % self.tname)
            return HTTPFound(location=self.request.route_url('sa_list',
                                                             table=self.tname))
        resp = action.create(self.request.dbsession, self.table)
        return {'sa_crud': resp,
                'relationships': self.relationships,
                'breadcrumbs': breadcrumbs(self.tname, 'sa_create')}

    @view_config(route_name='sa_read', renderer='/sacrud/read.jinja2')
    def sa_read(self):
        resp = action.CRUD(self.request.dbsession,
                           get_table(self.tname, self.request), pk=self.pk)
        return {'sa_crud': resp.read(),
                'breadcrumbs': breadcrumbs(self.tname, 'sa_read', id=self.pk)}

    @view_config(route_name='sa_update', renderer='/sacrud/create.jinja2')
    def sa_update(self):
        resp = action.CRUD(self.request.dbsession, self.table, self.pk)

        if 'form.submitted' in self.request.params:
            resp.request = self.params
            resp.update()
            self.flash_message("You updated object of %s" % self.tname)
            return HTTPFound(location=self.request.route_url('sa_list',
                                                             table=self.tname))
        return {'sa_crud': resp.update(),
                'pk_to_list': pk_to_list,
                'relationships': self.relationships,
                'breadcrumbs': breadcrumbs(self.tname, 'sa_update',
                                           id=self.pk)}

    @view_config(route_name='sa_delete')
    def sa_delete(self):
        action.CRUD(self.request.dbsession, self.table, pk=self.pk).delete()
        self.flash_message("You have removed object of %s" % self.tname)
        return HTTPFound(location=self.request.route_url('sa_list',
                                                         table=self.tname))
