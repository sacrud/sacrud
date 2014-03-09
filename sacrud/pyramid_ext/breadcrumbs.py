#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Breadcrumbs for sacrud pyramid extension.
"""


def breadcrumbs(tname,  view, id=None):
    bc = {}
    bc['sa_list'] = [{'name': 'Home', 'visible': True,
                      'view': 'sa_home',
                      'param': {'table': tname}},
                     {'name': tname, 'visible': True,
                      'view': 'sa_list',
                      'param': {'table': tname}}]

    bc['sa_create'] = bc['sa_list'][:]
    bc['sa_create'].append({'name': 'create',
                            'visible': False,
                            'view': 'sa_list',
                            'param': {'table': tname}})

    bc['sa_read'] = bc['sa_list'][:]
    bc['sa_read'].append({'name': id,
                          'visible': False,
                          'view': 'sa_list',
                          'param': {'table': tname}})

    bc['sa_update'] = bc['sa_read']

    bc['sa_union'] = bc['sa_list'][:]
    bc['sa_union'].append({'name': 'union',
                           'visible': False,
                           'view': 'sa_list',
                           'param': {'table': tname}})
    return bc[view]
