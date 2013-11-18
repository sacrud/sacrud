# -*- coding: utf-8 -*-
import sqlalchemy
import sqlalchemy.orm as orm
from ..version import __version__
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = None


def pkg_prefix(config):
    '''
    Function for return pkg prefix.

    >>> from pyramid.config import Configurator
    >>> settings = {'foo': 'foo', 'bar': 'bar'}

    # Create config
    >>> config = Configurator(settings=settings)

    # w/o route_prefix
    >>> pkg_prefix(config)
    '/sacrud/'

    # with route_prefix
    >>> config.route_prefix = "/admin"
    >>> pkg_prefix(config)
    ''
    '''
    return '' if config.route_prefix else '/sacrud/'


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

    config.include('pyramid_jinja2')
    config.add_static_view('/sa_static', 'sacrud:static')
    config.include(add_routes)
    config.add_jinja2_search_path("sacrud:templates")
    env = config.get_jinja2_environment()

    # if variable is None print '' instead of 'None'
    def _silent_none(value):
        if value is None:
            return ''
        return value
    env.finalize = _silent_none
    config.add_jinja2_extension('jinja2.ext.do')
    env.globals['str'] = str
    env.globals['getattr'] = getattr
    env.globals['isinstance'] = isinstance
    env.globals['sqlalchemy'] = sqlalchemy
    env.globals['session'] = DBSession
    env.globals['sacrud_ver'] = __version__
    config.scan()
