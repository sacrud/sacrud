#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Any helpers for Pyramid
"""

import os
import sqlalchemy

from pyramid.path import AssetResolver

from sacrud.common import import_from_string


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


def _silent_none(value):
    """
    >>> _silent_none(0)
    0
    >>> _silent_none('foo')
    'foo'
    >>> _silent_none(None)
    ''
    >>> _silent_none('None')
    ''
    >>> _silent_none(False)
    ''
    >>> class Foo(object):
    ...   def __bool__(self):
    ...     return False
    >>> _silent_none(Foo)
    <class 'sacrud.common.pyramid_helpers.Foo'>
    """
    if type(value) == int:
        return value
    if hasattr(value, '__bool__'):
        return value
    if not value:
        return ''
    try:
        if str(value) == 'None':
            return ''
    except UnicodeEncodeError:
        pass
    return value


def set_jinja2_silent_none(config):
    """ if variable is None print '' instead of 'None'
    """
    env = config.get_jinja2_environment()
    env.finalize = _silent_none


def get_settings_param(request, name):
    settings = request.registry.settings
    return settings[name]


def get_obj_from_settings(request, name):
    position_model = request.registry.settings\
        .get(name)
    if isinstance(position_model, basestring):
        return import_from_string(position_model)
    return position_model


def get_field_template(field):
    ar = AssetResolver()
    path = ar.resolve('sacrud:templates/sacrud/types/%s.jinja2' % field).abspath()
    if os.path.exists(path):
        return path
    return 'sacrud/types/String.jinja2'


def sacrud_env(fun):
    jinja2_globals = {'str': str, 'getattr': getattr, 'isinstance': isinstance,
                      'hasattr': hasattr,
                      'sqlalchemy': sqlalchemy,
                      'get_field_template': get_field_template}

    def wrapped(*args, **kwargs):
        response = fun(*args, **kwargs)
        if not isinstance(response, dict):
            return response
        DBSession = {'session': args[0].request.dbsession}
        response.update(jinja2_globals)
        response.update(DBSession)
        return response
    return wrapped
