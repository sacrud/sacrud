# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, orm
import unittest
from sacrud.tests.test_models import User, Profile, PHOTO_PATH, Base
from sacrud.action import get_relations, delete_fileobj, read, update, delete
from sacrud.action import get_pk, index, create
from pyramid.testing import DummyRequest
from StringIO import StringIO
import glob
import os
from zope.sqlalchemy import ZopeTransactionExtension
import transaction
from pyramid import testing
from pyramid.config import Configurator
from webtest.app import TestApp
from pyramid.url import route_url
from webtest.forms import Upload


class MockCGIFieldStorage(object):
    pass


class SacrudTests(unittest.TestCase):

    def setUp(self):

        request = testing.DummyRequest()
        config = testing.setUp(request=request)

        config.registry.settings['sqlalchemy.url'] = "sqlite:///:memory:"
        config.include('sacrud.pyramid_ext')
        settings = config.registry.settings
        settings['sacrud_models'] = (User, Profile)
        config.scan()

        from sacrud.pyramid_ext import DBSession
        engine = create_engine('sqlite:///:memory:')
        DBSession.configure(bind=engine)

        self.session = DBSession

        # To create tables, you typically do:
        #User.metadata.create_all(engine)
        User.metadata.create_all(engine)
        Profile.metadata.create_all(engine)

        self.app = config.make_wsgi_app()
        self.testapp = TestApp(self.app)

    def tearDown(self):
        def clear_files():
            for filename in glob.glob("%s/*.html" % (PHOTO_PATH, )):
                os.remove(os.path.join(PHOTO_PATH, filename))
        clear_files()
        self.session.remove()
        testing.tearDown()

    def user_add(self):
        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        transaction.commit()
        user = self.session.query(User).get(1)
        return user

    def profile_add(self, user):
        profile = Profile(user=user)
        self.session.add(profile)
        transaction.commit()
        profile = self.session.query(Profile).get(1)
        return profile

    def test_home_view(self):
        self.user_add()
        request = testing.DummyRequest()
        name = route_url('sa_home', request)
        response = self.testapp.get(name)
        self.failUnlessEqual(response.status, '200 OK')
        self.failUnlessEqual("Tables" in response, True)
        self.failUnlessEqual("user" in response, True)
        self.failUnlessEqual("profile" in response, True)

    def test_list_view(self):
        user = self.user_add()
        self.profile_add(user)
        
        request = testing.DummyRequest()
        name = route_url('sa_list', request, table="user")
        response = self.testapp.get(name)
        self.failUnlessEqual(response.status, '200 OK')
        name = route_url('sa_list', request, table="profile")
        response = self.testapp.get(name)
        self.failUnlessEqual(response.status, '200 OK')

    def test_read_view(self):
        user = self.user_add()
        self.profile_add(user)

        request = testing.DummyRequest()
        name = route_url('sa_read', request,
                                    table="user",
                                    id="1")
        response = self.testapp.get(name)
        self.failUnlessEqual(response.status, '200 OK')
        name = route_url('sa_read', request,
                                    table="profile", 
                                    id="1")
        response = self.testapp.get(name)
        self.failUnlessEqual(response.status, '200 OK')

    def test_create_view(self):
        request = testing.DummyRequest()
        name = route_url('sa_create', request,
                                      table="user")
        response = self.testapp.get(name)
        self.failUnlessEqual(response.status, '200 OK')

        form = response.form
        form['name'] = "Karlson"
        form['fullname'] = "Karlson the Third"
        form['password'] = 123
        response = form.submit("form.submitted").follow()

        self.failUnlessEqual(response.status, '200 OK')
        user = self.session.query(User).get(1)

        self.assertFalse(user is None)
        self.assertEqual(user.name,  "Karlson")
        self.assertEqual(user.fullname,  "Karlson the Third")
        self.assertEqual(user.password,  "123")

        name = route_url('sa_create', request,
                                      table="profile")

        response = self.testapp.get(name)
        form = response.form
        form['user_id'] = "1"
        form['phone'] = "123"
        form['cv'] = "Karlson live on the roof"
        field = form.get('married', index=0)
        field.checked = False

        form['salary'] = "200.23"
        upload = Upload('filename.txt', 'data')
        form['photo'] = upload

        response = form.submit("form.submitted").follow()

        self.failUnlessEqual(response.status, '200 OK')

        profile = self.session.query(Profile).get(1)

        self.assertFalse(profile is None)
        self.assertEqual(profile.user.id, 1)
        self.assertEqual(profile.phone,  "123")
        self.assertEqual(profile.cv, "Karlson live on the roof")
        self.assertEqual(profile.married,  False)
        self.assertEqual(profile.salary,  200.23)

    def test_update_view(self):
        user = self.user_add()
        self.profile_add(user)
        request = testing.DummyRequest()
        name = route_url('sa_update', request,
                                      table="user",
                                      id="1")
        response = self.testapp.get(name)
        self.failUnlessEqual(response.status, '200 OK')

        form = response.form
        form['name'] = "Karlson"
        form['fullname'] = "Karlson the Third"
        form['password'] = 123
        response = form.submit("form.submitted").follow()

        self.failUnlessEqual(response.status, '200 OK')
        user = self.session.query(User).get(1)

        self.assertFalse(user is None)
        self.assertEqual(user.name,  "Karlson")
        self.assertEqual(user.fullname,  "Karlson the Third")
        self.assertEqual(user.password,  "123")

        name = route_url('sa_update', request,
                                      table="profile",
                                      id="1")

        response = self.testapp.get(name)
        form = response.form
        form['user_id'] = "1"
        form['phone'] = "123"
        form['cv'] = "Karlson live on the roof"
        field = form.get('married', index=0)
        field.checked = False

        form['salary'] = "200.23"
        upload = Upload('filename.txt', 'data')
        form['photo'] = upload

        response = form.submit("form.submitted").follow()
        self.failUnlessEqual(response.status, '200 OK')
        
        profile = self.session.query(Profile).get(1)

        self.assertFalse(profile is None)
        self.assertEqual(profile.user.id, 1)
        self.assertEqual(profile.phone,  "123")
        self.assertEqual(profile.cv, "Karlson live on the roof")
        self.assertEqual(profile.married,  False)
        self.assertEqual(profile.salary,  200.23)

    def test_delete_view(self):
        user = self.user_add()
        self.profile_add(user)
        request = testing.DummyRequest()
        name = route_url('sa_delete', request,
                                      table="profile",
                                      id=1)
        response = self.testapp.get(name).follow()
        self.failUnlessEqual(response.status, '200 OK')

        name = route_url('sa_delete', request,
                                      table="user",
                                      id=1)
        response = self.testapp.get(name).follow()
        self.failUnlessEqual(response.status, '200 OK')
