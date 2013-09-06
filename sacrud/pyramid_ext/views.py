# -*- coding: utf-8 -*-
import ast
import sqlalchemy as sa
from sacrud import action
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from sacrud.pyramid_ext import DBSession


def breadcrumbs(tname,  view, id=None):
    bc = {}
    bc['sa_list'] = [{'name': 'Home', 'visible': True,
                      'view': 'sa_home',
                      'param': {'table': tname}},
                     {'name': tname, 'visible': True,
                      'view': 'sa_list',
                      'param': {'table': tname}}]
    bc['sa_create'] = bc['sa_list'][:]
    bc['sa_create'].append({'name': 'create',
                            'visible': False,
                            'view': 'sa_list',
                            'param': {'table': tname}})
    bc['sa_read'] = bc['sa_list'][:]
    bc['sa_read'].append({'name': id,
                          'visible': False,
                          'view': 'sa_list',
                          'param': {'table': tname}})
    bc['sa_update'] = bc['sa_read']
    bc['sa_union'] = bc['sa_list'][:]
    bc['sa_union'].append({'name': 'union',
                           'visible': False,
                           'view': 'sa_list',
                           'param': {'table': tname}})

    return bc[view]


def get_models(request):
    settings = request.registry.settings
    return settings['sacrud_models']


def get_table(tname, request):
    tables = get_models(request)
    return filter(lambda table: (table.__tablename__).
                  lower() == tname.lower(), tables)[0]


def get_relationship(tname, request):
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
    return {'tables': get_models(request)}


@view_config(route_name='sa_list', renderer='/sacrud/list.jinja2')
def sa_list(request):
    tname = request.matchdict['table']
    order_by = request.params.get('order_by', False)
    args = [DBSession, get_table(tname, request)]
    if order_by:
        args.append(order_by)
    resp = action.index(*args)
    return {'sa_crud': resp, 'breadcrumbs': breadcrumbs(tname, 'sa_list')}


@view_config(route_name='sa_create', renderer='/sacrud/create.jinja2')
def sa_create(request):
    tname = request.matchdict['table']
    if 'form.submitted' in request.params:
        action.create(DBSession, get_table(tname, request),
                      request.params.dict_of_lists())
        return HTTPFound(location=request.route_url('sa_list', table=tname))
    resp = action.create(DBSession, get_table(tname, request))
    rel = get_relationship(tname, request)
    return {'sa_crud': resp, 'rel': rel,
            'breadcrumbs': breadcrumbs(tname, 'sa_create')}


@view_config(route_name='sa_read', renderer='/sacrud/read.jinja2')
def sa_read(request):
    tname = request.matchdict['table']
    id = request.matchdict['id']
    resp = action.read(DBSession, get_table(tname, request), id)
    return {'sa_crud': resp,
            'breadcrumbs': breadcrumbs(tname, 'sa_read', id=id)}


@view_config(route_name='sa_update', renderer='/sacrud/create.jinja2')
def sa_update(request):
    tname = request.matchdict['table']
    id = request.matchdict['id']
    if 'form.submitted' in request.params:
        action.update(DBSession, get_table(tname, request), id,
                      request.params.dict_of_lists())
        return HTTPFound(location=request.route_url('sa_list', table=tname))
    resp = action.update(DBSession, get_table(tname, request), id)
    rel = get_relationship(tname, request)
    return {'sa_crud': resp, 'rel': rel,
            'breadcrumbs': breadcrumbs(tname, 'sa_update', id=id)}


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


@view_config(route_name='sa_delete')
def sa_delete(request):
    tname = request.matchdict['table']
    id = request.matchdict['id']
    action.delete(DBSession, get_table(tname, request), id)
    return HTTPFound(location=request.route_url('sa_list', table=tname))


@view_config(route_name='sa_union_fields', renderer='/sacrud/compare.jinja2')
def sa_union_fields(request):
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
    resp = action.index(*args)

    sa_checked_row = request.POST.get('sa_checked_row', None).split(",")
    if '' not in sa_checked_row:
        compare_objs = map(int, sa_checked_row)
    else:
        return HTTPFound(location=request.route_url('sa_list', table=tname))
    return {'compare_objs': compare_objs, 'sa_crud': resp,
            'breadcrumbs': breadcrumbs(tname, 'sa_union')}
