# -*- coding: utf-8 -*-
import sqlalchemy
import sqlalchemy.orm as orm
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.engine import create_engine

pkg_name = 'sacrud'

DBSession = None


def add_routes(config):
    config.add_route('sa_home',     '/' + pkg_name)
    config.add_route('sa_list',     '/' + pkg_name + '/{table}')
    config.add_route('sa_create',   '/' + pkg_name + '/{table}/create')
    config.add_route('sa_read',     '/' + pkg_name + '/{table}/read/{id}')
    config.add_route('sa_update',   '/' + pkg_name + '/{table}/update/{id}')
    config.add_route('sa_delete',   '/' + pkg_name + '/{table}/delete/{id}')
    config.add_route('sa_paste',    '/' + pkg_name + '/{table}/paste/{id}/{target_id}')
    config.add_route('sa_paste_tmp',    '/' + pkg_name + '/{table}/paste/{id}')


def includeme(config):
    global DBSession
    engine = sqlalchemy.engine_from_config(config.registry.settings)
    if DBSession is None:
        DBSession = orm.scoped_session(
            orm.sessionmaker(extension=ZopeTransactionExtension()))
    DBSession.remove()
    DBSession.configure(bind=engine)

    config.include('pyramid_jinja2')
    config.add_static_view('sa_static', 'sacrud:static')
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
    config.scan()
