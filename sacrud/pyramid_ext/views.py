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
import sqlalchemy as sa
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from sacrud import action
from sacrud.common.paginator import get_paginator
from sacrud.common.pyramid_helpers import get_settings_param
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
    obj = get_table(tname, request)
    if not obj:
        return None
    # Build a list of only relationship properties
    relation_properties = filter(
        lambda p: isinstance(p, sa.orm.properties.RelationshipProperty),
        sa.orm.class_mapper(obj).iterate_properties
    )
    related_classes = [{'cls': prop.mapper.class_,
                        'col': list(prop.local_columns)[0]}
                       for prop in relation_properties]
    return related_classes


@view_config(route_name='sa_save_position', request_method='POST',
             renderer='json')
def sa_save_position(request):
    kwargs = dict(request.POST)
    session = request.dbsession
    position_model_path = request.registry.settings\
                                 .get('sacrud_dashboard_position_model')
    if position_model_path:
        parts = position_model_path.split(':')
        temp = __import__(parts[0], globals(), locals(), [parts[1], ], 0)
        PositionModel = getattr(temp, parts[1])
        # getattr(PositionModel, 'widget')
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
    tables = get_settings_param(request, 'sacrud.models')
    sacrud_dashboard_columns = request.registry.settings\
                                      .get('sacrud_dashboard_columns', 3)
    context = {'dashboard_columns': sacrud_dashboard_columns}
    position_model_path = request.registry.settings\
                                 .get('sacrud_dashboard_position_model')
    if position_model_path:
        parts = position_model_path.split(':')
        temp = __import__(parts[0], globals(), locals(), [parts[1], ], 0)
        PositionModel = getattr(temp, parts[1])
        items_list = {}
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
        context.update({'new_tables': items_list, })
    else:
        context.update({'tables': sorted(tables.iteritems(),
                                         key=operator.itemgetter(1)), })
    return context


def sarow_to_json(rows):
    def serializator(x):
        def serialize_date(value):
            import json
            if not value or isinstance(value, basestring):
                return value
            try:
                json.dump(value)
            except TypeError:
                return str(value)
            return value
        return {k: serialize_date(v) for k, v in x.items()}
    json_list = [x.__dict__ for x in rows.items]
    map(lambda x: x.pop("_sa_instance_state", None), json_list)
    json_list = map(lambda x: serializator(x), json_list)
    return json_list


@view_config(route_name='sa_list', renderer='/sacrud/list.jinja2')
def sa_list(request):
    tname = request.matchdict['table']
    order_by = request.params.get('order_by', False)
    table = get_table(tname, request)
    args = [request.dbsession, table]

    if order_by:
        args.append(order_by)

    items_per_page = getattr(table, 'items_per_page', 10)
    resp = action.list(*args, paginator=get_paginator(request, items_per_page))

    # if URL like /sacrud/tablename?json=on return json
    if request.GET.get('json', None):
        request.override_renderer = 'json'
        return sarow_to_json(resp['row'])
    return {'sa_crud': resp, 'breadcrumbs': breadcrumbs(tname, 'sa_list')}


class CRUD(object):

    def __init__(self, request):
        self.request = request
        self.tname = request.matchdict['table']
        self.table = get_table(self.tname, self.request)
        self.relationships = get_relationship(self.tname, self.request)
        self.id = request.matchdict.get('id')
        self.params = request.params.dict_of_lists()

    def flash_message(self, message, status="success"):
        if hasattr(self.request, 'session'):
            self.request.session.flash([message, status])

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
        resp = action.read(self.request.dbsession,
                           get_table(self.tname, self.request), self.id)
        return {'sa_crud': resp,
                'breadcrumbs': breadcrumbs(self.tname, 'sa_read', id=self.id)}

    @view_config(route_name='sa_update', renderer='/sacrud/create.jinja2')
    def sa_update(self):
        if 'form.submitted' in self.request.params:
            action.update(self.request.dbsession, self.table, self.id,
                          self.params)
            self.flash_message("You updated object of %s" % self.tname)
            return HTTPFound(location=self.request.route_url('sa_list',
                                                             table=self.tname))
        resp = action.update(self.request.dbsession, self.table, self.id)
        return {'sa_crud': resp,
                'relationships': self.relationships,
                'breadcrumbs': breadcrumbs(self.tname, 'sa_update',
                                           id=self.id)}

    @view_config(route_name='sa_delete')
    def sa_delete(self):
        action.delete(self.request.dbsession, self.table, self.id)
        self.flash_message("You have removed object of %s" % self.tname)
        return HTTPFound(location=self.request.route_url('sa_list',
                                                         table=self.tname))


@view_config(route_name='sa_paste', renderer='/sacrud/list.jinja2')
def sa_paste(request):
    tname = request.matchdict['table']
    id = request.matchdict['id']
    target_id = request.matchdict['target_id']

    source_obj = action.read(request.dbsession, get_table(tname, request),
                             id)['obj']
    pos_name = source_obj.__mapper_args__['order_by']
    action.update(request.dbsession, get_table(tname, request), target_id,
                  {pos_name: [getattr(source_obj, pos_name)]})

    return HTTPFound(location=request.route_url('sa_list', table=tname))
