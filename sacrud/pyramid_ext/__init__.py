#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Includeme of SACRUD
"""
import sqlalchemy
import sqlalchemy.orm as orm
from zope.sqlalchemy import ZopeTransactionExtension

from sacrud.common.pyramid_helpers import (get_obj_from_settings, pkg_prefix,
                                           set_jinja2_silent_none)


def add_routes(config):
    prefix = pkg_prefix(config)
    config.add_route('sa_home',           prefix)
    config.add_route('sa_save_position',  prefix + 'save_position')
    config.add_route('sa_list',           prefix + '{table}')
    config.add_route('sa_create',         prefix + '{table}/create')
    config.add_route('sa_update',         prefix + '{table}/update/*pk')
    config.add_route('sa_delete',         prefix + '{table}/delete/*pk')


def includeme(config):
    engine = sqlalchemy.engine_from_config(config.registry.settings)
    DBSession = orm.scoped_session(
        orm.sessionmaker(extension=ZopeTransactionExtension()))
    DBSession.configure(bind=engine)

    config.set_request_property(lambda x: DBSession, 'dbsession', reify=True)
    config.set_request_property(
        lambda x: get_obj_from_settings(x, 'sacrud.dashboard_position_model'),
        'sacrud_dashboard_position_model', reify=True)

    # Jinja2
    config.add_jinja2_search_path("sacrud:templates")
    config.add_jinja2_extension('jinja2.ext.loopcontrols')
    set_jinja2_silent_none(config)

    config.include(add_routes)
    config.add_static_view('/sa_static', 'sacrud:static')
    config.scan()
