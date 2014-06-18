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
import os
import sqlalchemy
import sqlalchemy.orm as orm
from webassets import Bundle
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


def add_webasset(config):
    curdir = os.path.dirname(os.path.abspath(__file__))
    settings = config.registry.settings
    settings["webassets.base_dir"] = os.path.join(curdir, '..', 'static')
    settings["webassets.base_url"] = "/admin/sa_static"
    settings["webassets.debug"] = "True"
    settings["webassets.updater"] = "timestamp"
    settings["webassets.jst_compiler"] = "Handlebars.compile"
    settings["webassets.url_expire"] = "False"
    settings["webassets.static_view"] = "True"
    settings["webassets.cache_max_age"] = 3600

    config.include('pyramid_webassets')

    css_base = Bundle('css/*.css', 'css/**/*.css',
                      filters='cssmin',
                      output='css/_base.css', debug=False)

    config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
    assets_env = config.get_webassets_env()
    jinja2_env = config.get_jinja2_environment()
    jinja2_env.assets_environment = assets_env
    config.add_webasset('sa_css', css_base)


def includeme(config):
    engine = sqlalchemy.engine_from_config(config.registry.settings)
    DBSession = orm.scoped_session(
        orm.sessionmaker(extension=ZopeTransactionExtension()))
    DBSession.configure(bind=engine)
    config.set_request_property(lambda x: DBSession, 'dbsession', reify=True)

    # Dashboard widget
    settings = config.registry.settings
    if 'sacrud_dashboard_position_model' not in settings:
        settings['sacrud_dashboard_position_model'] = get_obj_from_settings(settings,
                                                                            'sacrud.dashboard_position_model')

    # Jinja2
    config.add_jinja2_search_path("sacrud:templates")
    config.add_jinja2_extension('jinja2.ext.loopcontrols')

    # Routes
    config.include(add_routes)
    config.add_static_view('sa_static', 'sacrud:static')

    # Assets
    config.include(add_webasset)

    config.scan()
