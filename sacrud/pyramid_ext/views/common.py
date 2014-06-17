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
from collections import OrderedDict

from pyramid.view import view_config
from sqlalchemy import and_, case

from sacrud.common.pyramid_helpers import get_settings_param


@view_config(route_name='sa_save_position', request_method='POST',
             renderer='json')
def sa_save_position(request):
    """ col1 col2 col3
         w1   w2   w3
         w4   w5
         w7

    Example w4 move to col3 after w3:
        w6 and w9 position = position + 3
        w4 = 2*3 - 3 + 3 = 6

    Example w4 move to col2 after w2:
        w5 and w8 position = position + 3
        w4 = 2*3 - 3 + 2 = 5

    Example w5 move to col1 after w4:
        w7 position = position + 3
        w5 = 3*3 - 3 + 1 = 7

    Example w5 move to col2 to top:
        w2 and w8 position = position + 3
        w5 = 1*3 - 3 + 2 = 2
    """
    kwargs = dict(request.POST)
    session = request.dbsession
    columns = request.registry.settings\
        .get('sacrud_dashboard_columns', 3)
    PositionModel = request.registry.settings\
        .get('sacrud_dashboard_position_model', None)
    if not PositionModel:
        return
    PositionModel = PositionModel.__table__

    widget = session.query(PositionModel)\
        .filter_by(widget=kwargs['widget'] or None).one()
    old_position = widget.position
    position = (int(kwargs['position']) + 1) * columns - columns + int(kwargs['column'])
    if old_position == position:
        return
    # do position negative for replace unique value
    session.query(PositionModel).update({'position': -PositionModel.c.position},
                                        synchronize_session=False)
    session.execute(
        PositionModel.update(
        ).values(
            position=case(
                [
                    # change nodes position after widget
                    (and_(-PositionModel.c.position % columns == position % columns,
                          -PositionModel.c.position >= position,
                          -PositionModel.c.position % columns == position % columns,
                          -PositionModel.c.position % columns != old_position % columns,
                          PositionModel.c.id != widget.id),
                     -PositionModel.c.position + columns),
                    # change widget position
                    (PositionModel.c.id == widget.id, position),
                    # change old nodes position after widget
                    (and_(-PositionModel.c.position % columns == old_position % columns,
                          -PositionModel.c.position >= old_position,
                          position % columns != old_position % columns,
                          PositionModel.c.id != widget.id),
                     -PositionModel.c.position - columns),
                    # change nodes position if move to same col
                    (and_(-PositionModel.c.position >= position,
                          -PositionModel.c.position <= old_position,
                          -PositionModel.c.position % columns == position % columns,
                          -PositionModel.c.position % columns == old_position % columns,
                          PositionModel.c.id != widget.id),
                     -PositionModel.c.position + columns),
                    # change nodes position if move to same col
                    (and_(position > old_position,
                          -PositionModel.c.position >= old_position,
                          -PositionModel.c.position <= position,
                          -PositionModel.c.position % columns == position % columns,
                          -PositionModel.c.position % columns == old_position % columns,
                          PositionModel.c.id != widget.id),
                     -PositionModel.c.position - columns)
                ],
                else_=-PositionModel.c.position
            )
        )
    )
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
