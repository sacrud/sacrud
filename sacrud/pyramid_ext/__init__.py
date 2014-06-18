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

from sacrud.common.pyramid_helpers import get_obj_from_settings, pkg_prefix


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
    settings = config.registry.settings

    # Dashboard widget
    settings = config.registry.settings
    if 'sacrud_dashboard_position_model' not in settings:
        settings['sacrud_dashboard_position_model'] = get_obj_from_settings(settings,
                                                                            'sacrud.dashboard_position_model')

    # Jinja2
    config.add_jinja2_search_path("sacrud:templates")
    config.add_jinja2_extension('jinja2.ext.loopcontrols')

    config.include(add_routes)
    config.add_static_view('sa_static', 'sacrud:static')
    config.scan()
