# -*- coding: utf-8 -*-
import ast
import itertools
import sqlalchemy as sa

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from sacrud import action
from sacrud.pyramid_ext import DBSession
from sacrud.pyramid_ext.breadcrumbs import breadcrumbs
from sacrud.common.paginator import get_paginator
from sacrud.common.pyramid_helpers import get_settings_param


def get_table(tname, request):
    """ Return table by table name from sacrud.models in settings.
    """
    # TODO: write test
    # convert values of models dict to flat list
    tables = itertools.chain(*get_settings_param(request, 'sacrud.models').values())
    return filter(lambda table: (table.__tablename__).
                  lower() == tname.lower(), tables)[0]


def get_relationship(tname, request):
    # TODO: write test
    obj = get_table(tname, request)
    # Build a list of only relationship properties
    relation_properties = filter(
        lambda p: isinstance(p, sa.orm.properties.RelationshipProperty),
        sa.orm.class_mapper(obj).iterate_properties
    )
    #related_tables = [prop.target for prop in relation_properties]
    related_classes = [{'cls': prop.mapper.class_,
                        'col': list(prop.local_columns)[0]}
                       for prop in relation_properties]
    return related_classes


@view_config(route_name='sa_home', renderer='/sacrud/home.jinja2')
def sa_home(request):
    return {'tables': get_settings_param(request, 'sacrud.models')}


@view_config(route_name='sa_list', renderer='/sacrud/list.jinja2')
def sa_list(request):
    tname = request.matchdict['table']
    order_by = request.params.get('order_by', False)
    args = [DBSession, get_table(tname, request)]

    if order_by:
        args.append(order_by)
    resp = action.list(*args, paginator=get_paginator(request))
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
            action.create(DBSession, self.table,
                          self.request.params.dict_of_lists())
            self.flash_message("You created new object of %s" % self.tname)
            return HTTPFound(location=self.request.route_url('sa_list', table=self.tname))
        resp = action.create(DBSession, self.table)
        return {'sa_crud': resp,
                'relationships': self.relationships,
                'breadcrumbs': breadcrumbs(self.tname, 'sa_create')}

    @view_config(route_name='sa_read', renderer='/sacrud/read.jinja2')
    def sa_read(self):
        resp = action.read(DBSession,
                           get_table(self.tname, self.request), self.id)
        return {'sa_crud': resp,
                'breadcrumbs': breadcrumbs(self.tname, 'sa_read', id=self.id)}

    @view_config(route_name='sa_update', renderer='/sacrud/create.jinja2')
    def sa_update(self):
        if 'form.submitted' in self.request.params:
            action.update(DBSession, self.table, self.id, self.params)
            self.flash_message("You updated object of %s" % self.tname)
            return HTTPFound(location=self.request.route_url('sa_list', table=self.tname))
        resp = action.update(DBSession, self.table, self.id)
        return {'sa_crud': resp,
                'relationships': self.relationships,
                'breadcrumbs': breadcrumbs(self.tname, 'sa_update', id=self.id)}

    @view_config(route_name='sa_delete')
    def sa_delete(self):
        action.delete(DBSession, self.table, self.id)
        self.flash_message("You have removed object of %s" % self.tname)
        return HTTPFound(location=self.request.route_url('sa_list', table=self.tname))


@view_config(route_name='sa_paste', renderer='/sacrud/list.jinja2')
def sa_paste(request):
    tname = request.matchdict['table']
    id = request.matchdict['id']
    target_id = request.matchdict['target_id']

    source_obj = action.read(DBSession, get_table(tname, request), id)['obj']
    pos_name = source_obj.__mapper_args__['order_by']
    action.update(DBSession, get_table(tname, request), target_id,
                  {pos_name: [getattr(source_obj, pos_name)]})

    return HTTPFound(location=request.route_url('sa_list', table=tname))


@view_config(route_name='sa_union_fields', renderer='/sacrud/compare.jinja2')
def sa_union_fields(request):
    # XXX: experimental future
    tname = request.matchdict['table']
    table = get_table(tname, request)
    pk = action.get_pk(table)
    if 'form.submitted' in request.params and pk:
        comp_objs = ast.literal_eval(request.POST['sa_comp_objs'])
        new_row_param = {}
        for field in request.POST:
            if 'sa_col_' not in field:
                continue
            row_name = field.replace("sa_col_", "")
            row_id_for_value = request.POST[field]
            row_value = DBSession.query(getattr(table, row_name))\
                                 .filter(
                                     getattr(table, pk) == row_id_for_value
                                 ).one()
            new_row_param[row_name] = [row_value, ]
        # delete rows
        for id in comp_objs:
            action.delete(DBSession, table, id)
        # add new union row
        action.create(DBSession, table, new_row_param)
        return HTTPFound(location=request.route_url('sa_list', table=tname))

    order_by = request.params.get('order_by', False)
    args = [DBSession, table]
    if order_by:
        args.append(order_by)
    resp = action.list(*args)

    sa_checked_row = request.POST.get('sa_checked_row', None).split(",")
    if '' not in sa_checked_row:
        compare_objs = map(int, sa_checked_row)
    else:
        return HTTPFound(location=request.route_url('sa_list', table=tname))
    return {'compare_objs': compare_objs, 'sa_crud': resp,
            'breadcrumbs': breadcrumbs(tname, 'sa_union')}
