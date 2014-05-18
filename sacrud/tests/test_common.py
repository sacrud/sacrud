#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Test for sacrud.common
"""

import unittest

from pyramid.testing import DummyRequest
from webhelpers.paginate import PageURL_WebOb

from sacrud.common import import_from_string
from sacrud.common.custom import as_link, get_name, horizontal_field
from sacrud.common.paginator import get_current_page, get_paginator
from sacrud.tests.test_models import User


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.request = DummyRequest()

    def tearDown(self):
        pass


class PaginatorTest(BaseTest):

    def test_get_current_page(self):
        page = get_current_page(self.request)
        self.assertEqual(page, 1)
        self.request.GET['page'] = 5
        page = get_current_page(self.request)
        self.assertEqual(page, 5)

    def test_get_paginator(self):
        paginator = get_paginator(self.request)
        self.assertEqual(paginator['items_per_page'], 10)
        self.assertEqual(paginator['page'], 1)
        self.assertEqual(type(paginator['url']), PageURL_WebOb)

        self.request.GET['page'] = 100500
        paginator = get_paginator(self.request, 20)
        self.assertEqual(paginator['items_per_page'], 20)
        self.assertEqual(paginator['page'], 100500)
        self.assertEqual(type(paginator['url']), PageURL_WebOb)


class CustomTest(BaseTest):

    def test_horizontal_field(self):
        widget = horizontal_field(sacrud_name='foo')
        self.assertEqual(widget,
                         {'info': {'sacrud_list_template': 'sacrud/custom/HorizontalFieldsList.jinja2',
                                   'sacrud_position': 'inline',
                                   'sacrud_template': 'sacrud/custom/HorizontalFieldsDetail.jinja2'},
                          'sacrud_name': 'foo', 'name': '', 'horizontal_columns': ()})
        widget = horizontal_field('a', 'b', sacrud_name='foo')
        self.assertEqual(widget,
                         {'info': {'sacrud_list_template': 'sacrud/custom/HorizontalFieldsList.jinja2',
                                   'sacrud_position': 'inline',
                                   'sacrud_template': 'sacrud/custom/HorizontalFieldsDetail.jinja2'},
                          'sacrud_name': 'foo', 'name': '', 'horizontal_columns': ('a', 'b')})
        widget = horizontal_field()
        self.assertEqual(widget,
                         {'info': {'sacrud_list_template': 'sacrud/custom/HorizontalFieldsList.jinja2',
                                   'sacrud_position': 'inline',
                                   'sacrud_template': 'sacrud/custom/HorizontalFieldsDetail.jinja2'},
                          'sacrud_name': '', 'name': '', 'horizontal_columns': ()})

    def test_get_name(self):
        self.assertEqual('sex', get_name(User.sex))
        self.assertEqual('id', get_name(User.id))
        self.assertEqual('user password', get_name(User.password))

        class EmptyType: pass
        foo = EmptyType()
        foo.info = {}
        foo.name = ''
        self.assertEqual('', get_name(foo))

    def test_as_link(self):
        link = as_link(User.sex)
        self.assertEqual(link['info'],
                         {'sacrud_list_template': 'sacrud/custom/AsLinkList.jinja2',
                          'sacrud_position': 'inline'})
        self.assertEqual(link['column'], User.sex)
        self.assertEqual(link['name'], 'sex')
        self.assertEqual(link['sacrud_name'], '')

        link = as_link(User.sex, sacrud_name=u'foo bar баз')
        self.assertEqual(link['info'],
                         {'sacrud_list_template': 'sacrud/custom/AsLinkList.jinja2',
                          'sacrud_position': 'inline'})
        self.assertEqual(link['column'], User.sex)
        self.assertEqual(link['name'], 'sex')
        self.assertEqual(link['sacrud_name'], u'foo bar \u0431\u0430\u0437')


class CommonTest(BaseTest):

    def test_import_from_string(self):
        self.assertEqual(User,
                         import_from_string('sacrud.tests.test_models:User'))
