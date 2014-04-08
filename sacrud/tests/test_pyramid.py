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

from pyramid import testing
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from sacrud.pyramid_ext.breadcrumbs import breadcrumbs, get_crumb
from sacrud.tests.test_models import User, Profile

from sacrud.pyramid_ext.views import get_table

TEST_DATABASE_CONNECTION_STRING = "sqlite:///:memory:"
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        config = testing.setUp(request=self.request)
        config.registry.settings['sqlalchemy.url'] = TEST_DATABASE_CONNECTION_STRING
        engine = create_engine(TEST_DATABASE_CONNECTION_STRING)
        DBSession.remove()
        DBSession.configure(bind=engine)
        config.include('sacrud.pyramid_ext', route_prefix='/admin')
        settings = config.registry.settings
        settings['sacrud.models'] = {'': [User], 'auth': [User, Profile]}

    def tearDown(self):
        testing.tearDown()


class BreadCrumbsTest(BaseTest):

    def test_get_crumb(self):
        crumb = get_crumb('Home', True, 'sa_home', {'table': 'foo'})
        self.assertEqual(crumb, {'visible': True, 'name': 'Home',
                                 'param': {'table': 'foo'},
                                 'view': 'sa_home'})

    def test_breadcrumbs(self):
        bc = breadcrumbs('foo', 'sa_list')
        self.assertEqual(bc,
                         [{'visible': True, 'name': 'Home',
                           'param': {'table': 'foo'},
                           'view': 'sa_home'},
                          {'visible': True, 'name': 'foo',
                           'param': {'table': 'foo'}, 'view': 'sa_list'}])
        bc = breadcrumbs('foo', 'sa_create')
        self.assertEqual(bc, [{'visible': True, 'name': 'Home',
                               'param': {'table': 'foo'}, 'view': 'sa_home'},
                              {'visible': True, 'name': 'foo',
                               'param': {'table': 'foo'}, 'view': 'sa_list'},
                              {'visible': False, 'name': 'create',
                               'param': {'table': 'foo'}, 'view': 'sa_list'}])
        bc = breadcrumbs('foo', 'sa_read')
        self.assertEqual(bc, [{'visible': True, 'name': 'Home',
                               'param': {'table': 'foo'}, 'view': 'sa_home'},
                              {'visible': True, 'name': 'foo',
                               'param': {'table': 'foo'}, 'view': 'sa_list'},
                              {'visible': False, 'name': None,
                               'param': {'table': 'foo'}, 'view': 'sa_list'}])
        bc = breadcrumbs('foo', 'sa_union')
        self.assertEqual(bc, [{'visible': True, 'name': 'Home',
                               'param': {'table': 'foo'}, 'view': 'sa_home'},
                              {'visible': True, 'name': 'foo',
                               'param': {'table': 'foo'}, 'view': 'sa_list'},
                              {'visible': False, 'name': 'union',
                               'param': {'table': 'foo'}, 'view': 'sa_list'}])


class ViewsTest(BaseTest):

    def test_get_table(self):
        user = get_table('user', self.request)
        self.assertEqual(user, User)
        foo = get_table('foo', self.request)
        self.assertEqual(foo, None)
