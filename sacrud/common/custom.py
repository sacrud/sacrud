#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Any instruments for customizing Models
"""


def hosrizontal_field(*args, **kwargs):
    sacrud_name = ''
    if 'sacrud_name' in kwargs:
        sacrud_name = kwargs['sacrud_name']
    return {'info': {'sacrud_position': 'inline',
                     'sacrud_template': 'sacrud/custom/HorizontalFields.jinja2'},
            'horizontal_columns': args,
            'sacrud_name': sacrud_name,
            'name': '',
            }
