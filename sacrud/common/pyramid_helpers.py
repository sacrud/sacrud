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


def set_jinja2_silent_none(config):
    """ if variable is None print '' instead of 'None'
    """
    env = config.get_jinja2_environment()

    def _silent_none(value):
        if not value or value == 'None':
            return ''
        return value
    env.finalize = _silent_none


def set_jinja2_globals(config, hashes):
    """ add globals to context
    """
    env = config.get_jinja2_environment()
    env.globals.update(hashes)
