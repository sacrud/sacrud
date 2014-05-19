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


def get_name(column):
    if 'verbose_name' in column.info:
        return column.info['verbose_name']
    if column.name:
        return column.name
    return ''


def horizontal_field(*args, **kwargs):
    """
    :Examples:

    >>> horizontal_field(sacrud_name='foo')
    {'info': {'sacrud_list_template': 'sacrud/custom/HorizontalFieldsList.jinja2', 'sacrud_position': 'inline', 'sacrud_template': 'sacrud/custom/HorizontalFieldsDetail.jinja2'}, 'sacrud_name': 'foo', 'name': '', 'horizontal_columns': ()}
    >>> horizontal_field('a', 'b', sacrud_name='foo')
    {'info': {'sacrud_list_template': 'sacrud/custom/HorizontalFieldsList.jinja2', 'sacrud_position': 'inline', 'sacrud_template': 'sacrud/custom/HorizontalFieldsDetail.jinja2'}, 'sacrud_name': 'foo', 'name': '', 'horizontal_columns': ('a', 'b')}
    >>> horizontal_field()
    {'info': {'sacrud_list_template': 'sacrud/custom/HorizontalFieldsList.jinja2', 'sacrud_position': 'inline', 'sacrud_template': 'sacrud/custom/HorizontalFieldsDetail.jinja2'}, 'sacrud_name': '', 'name': '', 'horizontal_columns': ()}

    """
    sacrud_name = ''
    if 'sacrud_name' in kwargs:
        sacrud_name = kwargs['sacrud_name']
    return {'info': {'sacrud_position': 'inline',
                     'sacrud_template': 'sacrud/custom/HorizontalFieldsDetail.jinja2',
                     'sacrud_list_template': 'sacrud/custom/HorizontalFieldsList.jinja2',
                     },
            'horizontal_columns': args,
            'sacrud_name': sacrud_name,
            'name': '',
            }


def as_link(column, *args, **kwargs):
    sacrud_name = ''
    if 'sacrud_name' in kwargs:
        sacrud_name = kwargs['sacrud_name']
    return {'info': {'sacrud_position': 'inline',
                     'sacrud_list_template': 'sacrud/custom/AsLinkList.jinja2',
                     },
            'column': column,
            'sacrud_name': sacrud_name,
            'name': get_name(column),
            }
