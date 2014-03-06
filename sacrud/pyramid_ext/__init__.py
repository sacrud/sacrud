# -*- coding: utf-8 -*-
import os
import sqlalchemy
import sqlalchemy.orm as orm

from zope.sqlalchemy import ZopeTransactionExtension
from pyramid.path import AssetResolver

from sacrud.version import __version__
from sacrud.common.pyramid_helpers import (
    pkg_prefix,
    set_jinja2_silent_none,
    set_jinja2_globals,
)

DBSession = None


def get_field_template(field):
    ar = AssetResolver()
    path = ar.resolve('sacrud:templates/sacrud/types/%s.jinja2' % field).abspath()
    if os.path.exists(path):
        return path
    return 'sacrud/types/String.jinja2'


def add_routes(config):
    prefix = pkg_prefix(config)
    config.add_route('sa_home',     prefix)
    config.add_route('sa_list',     prefix + '{table}')
    config.add_route('sa_create',   prefix + '{table}/create')
    config.add_route('sa_read',     prefix + '{table}/read/{id}')
    config.add_route('sa_update',   prefix + '{table}/update/{id}')
    config.add_route('sa_delete',   prefix + '{table}/delete/{id}')
    config.add_route('sa_paste',    prefix + '{table}/paste/{id}/' +
                                             '{target_id}')
    config.add_route('sa_paste_tmp', prefix + '{table}/paste/{id}')
    config.add_route('sa_union_fields', prefix + '{table}/union')


def includeme(config):
    global DBSession
    engine = sqlalchemy.engine_from_config(config.registry.settings)
    if DBSession is None:
        DBSession = orm.scoped_session(
            orm.sessionmaker(extension=ZopeTransactionExtension()))
    DBSession.remove()
    DBSession.configure(bind=engine)

    config.include(add_routes)
    config.include('pyramid_jinja2')
    config.add_static_view('/sa_static', 'sacrud:static')
    config.add_jinja2_search_path("sacrud:templates")

    set_jinja2_silent_none(config)

    jinja2_globals = {'str': str, 'getattr': getattr, 'isinstance': isinstance,
                      'hasattr': hasattr,
                      'session': DBSession,
                      'sqlalchemy': sqlalchemy,
                      'sacrud_ver': __version__,
                      'get_field_template': get_field_template}
    set_jinja2_globals(config, jinja2_globals)
    config.scan()
