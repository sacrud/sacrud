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


class MockCGIFieldStorage(object):
    pass


class SacrudTests(unittest.TestCase):

    def setUp(self):

        engine = create_engine('sqlite:///:memory:')
        DBSession = orm.scoped_session(
                                       orm.sessionmaker(extension=ZopeTransactionExtension()))

        DBSession.remove()
        DBSession.configure(bind=engine)

        session = DBSession
        self.session = session
    
        request = testing.DummyRequest()
        config = testing.setUp(request=request)

        config.registry.settings['sqlalchemy.url'] = "sqlite:///:memory:"
        config.include('sacrud.pyramid_ext')
        settings = config.registry.settings
        settings['sacrud_models'] = (User, Profile)
        config.scan()

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

    def add_user(self):
        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        transaction.commit()
        user = self.session.query(User).get(1)
        return user

    def test_home_view(self):
        self.add_user()
        request = testing.DummyRequest()
        name = route_url('sa_home', request)
        response = self.testapp.get(name)
        self.failUnlessEqual(response.status, '200 OK')
        self.failUnlessEqual("Tables" in response, True)
        self.failUnlessEqual("user" in response, True)
        self.failUnlessEqual("profile" in response, True)
        response = response.click(linkid="id_user").follow()
        self.failUnlessEqual(response.status, '200 OK')
        response = self.testapp.get(name)
        response = response.click(linkid="id_profile").follow()
        self.failUnlessEqual(response.status, '200 OK')

    def test_list_view(self):
        pass

    def test_add_view(self):
        pass

    def test_update_view(self):
        pass
    
    def test_delete_view(self):
        pass