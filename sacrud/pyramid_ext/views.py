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
    tables = itertools.chain(
        *get_settings_param(request, 'sacrud.models').values())
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
    # related_tables = [prop.target for prop in relation_properties]
    related_classes = [{'cls': prop.mapper.class_,
                        'col': list(prop.local_columns)[0]}
                       for prop in relation_properties]
    return related_classes


@view_config(route_name='sa_home', renderer='/sacrud/home.jinja2')
def sa_home(request):
    return {'tables': get_settings_param(request, 'sacrud.models')}


def sarow_to_json(rows):
    def serializator(x):
        def serialize_date(value):
            import datetime
            if isinstance(value, (datetime.datetime, datetime.date)):
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
    args = [request.dbsession, get_table(tname, request)]

    if order_by:
        args.append(order_by)
    resp = action.list(*args, paginator=get_paginator(request))

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

    def flash_message(self, message):
        if hasattr(self.request, 'session'):
            self.request.session.flash(message)

    @view_config(route_name='sa_create', renderer='/sacrud/create.jinja2')
    def sa_create(self):
        if 'form.submitted' in self.request.params:
            action.create(self.request.dbsession, self.table,
                          self.request.params.dict_of_lists())
            self.flash_message("You created new object of %s" % self.tname)
            return HTTPFound(location=self.request.route_url('sa_list', table=self.tname))
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
            action.update(self.request.dbsession, self.table, self.id, self.params)
            self.flash_message("You updated object of %s" % self.tname)
            return HTTPFound(location=self.request.route_url('sa_list', table=self.tname))
        resp = action.update(self.request.dbsession, self.table, self.id)
        return {'sa_crud': resp,
                'relationships': self.relationships,
                'breadcrumbs': breadcrumbs(self.tname, 'sa_update', id=self.id)}

    @view_config(route_name='sa_delete')
    def sa_delete(self):
        action.delete(self.request.dbsession, self.table, self.id)
        self.flash_message("You have removed object of %s" % self.tname)
        return HTTPFound(location=self.request.route_url('sa_list', table=self.tname))


@view_config(route_name='sa_paste', renderer='/sacrud/list.jinja2')
def sa_paste(request):
    tname = request.matchdict['table']
    id = request.matchdict['id']
    target_id = request.matchdict['target_id']

    source_obj = action.read(request.dbsession, get_table(tname, request), id)['obj']
    pos_name = source_obj.__mapper_args__['order_by']
    action.update(request.dbsession, get_table(tname, request), target_id,
                  {pos_name: [getattr(source_obj, pos_name)]})

    return HTTPFound(location=request.route_url('sa_list', table=tname))
