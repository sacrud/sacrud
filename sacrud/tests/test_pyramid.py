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

import os
import unittest

from pyramid import testing

from sacrud.pyramid_ext.breadcrumbs import breadcrumbs, get_crumb
from sacrud.pyramid_ext.views import get_relationship, get_table
from sacrud.tests.test_models import (_initTestingDB, DB_FILE, Profile,
                                      TEST_DATABASE_CONNECTION_STRING, User,
                                      user_add, profile_add)


class BaseTest(unittest.TestCase):

    def setUp(self):
        from sacrud.tests.mock_main import main
        settings = {'sqlalchemy.url': TEST_DATABASE_CONNECTION_STRING}
        app = main({}, **settings)
        DBSession = _initTestingDB()
        user_add(DBSession)
        user_add(DBSession)
        user = user_add(DBSession)
        #profile_add(DBSession, user)

        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        del self.testapp
        from sacrud.tests.test_models import DBSession
        DBSession.remove()
        os.remove(DB_FILE)


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
    def _include_sacrud(self):
        request = testing.DummyRequest()
        config = testing.setUp(request=request)
        config.registry.settings['sqlalchemy.url'] = TEST_DATABASE_CONNECTION_STRING
        config.include('sacrud.pyramid_ext', route_prefix='/admin')
        settings = config.registry.settings
        settings['sacrud.models'] = {'': [User], 'auth': [User, Profile]}
        return request

    def test_get_table(self):
        request = self._include_sacrud()
        user = get_table('UsEr', request)
        self.assertEqual(user, User)
        foo = get_table('foo', request)
        self.assertEqual(foo, None)

    def test_get_relationship(self):
        request = self._include_sacrud()
        foo = get_relationship('foo', request)
        self.assertEqual(foo, None)
        bar = get_relationship('user', request)
        self.assertEqual(len(bar), 1)
        self.assertEqual(bar, [{'col': User.id, 'cls': Profile}])

    def test_sa_home(self):
        res = self.testapp.get('/admin/', status=200)
        self.failUnless('Auth models' in res.body)
        self.failUnless('<a id="id_user" href="http://localhost/admin/user">user</a>' in res.body)
        self.failUnless('<a id="id_profile" href="http://localhost/admin/profile">profile</a>' in res.body)

    def test_sa_list(self):
        res = self.testapp.get('/admin/user', status=200)
        self.failUnless('user list' in res.body)
        res = self.testapp.get('/admin/profile', status=200)
        self.failUnless('profile list' in res.body)

    def test_sa_read(self):
        res = self.testapp.get('/admin/user/read/1', status=200)
        self.failUnless('view user' in res.body)

    def test_sa_update(self):
        res = self.testapp.get('/admin/user/update/1', status=200)
        self.failUnless('edit user' in res.body)

    def test_sa_create(self):
        res = self.testapp.get('/admin/user/create', status=200)
        self.failUnless('create' in res.body)
        self.failUnless('edit user' in res.body)

    def test_sa_delete(self):
        res = self.testapp.get('/admin/user/read/1', status=200)
        self.failUnless('view user' in res.body)
        self.testapp.get('/admin/user/delete/1', status=302)
