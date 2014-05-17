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

    """
    if type(value) == int:
        return value
    if hasattr(value, '__bool__'):
        return value
    if not value or value == 'None':
        return ''
    return value


def set_jinja2_silent_none(config):
    """ if variable is None print '' instead of 'None'
    """
    env = config.get_jinja2_environment()
    env.finalize = _silent_none


def set_jinja2_globals(config, hashes):
    """ add globals to context
    """
    env = config.get_jinja2_environment()
    env.globals.update(hashes)


def get_settings_param(request, name):
    settings = request.registry.settings
    if 'sacrud_models' in settings:
        message = 'WARNING: Use "sacrud.models" key setting instead "sacrud_models !!!' +\
                  ' This new requirements for sacrud >= 0.1.1 version"'
        print '\033[93m' + message + '\033[0m'
        raise Exception(message)
    return settings[name]


def get_obj_from_settings(request, name):
    position_model = request.registry.settings\
        .get(name)
    if isinstance(position_model, basestring):
        return import_from_string(position_model)
    return position_model
