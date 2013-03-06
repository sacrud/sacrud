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
from sacrud.pyramid_ext.views import sa_home
from pyramid.config import Configurator
from paste.deploy.loadwsgi import appconfig


class MockCGIFieldStorage(object):
    pass


here = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(here, 'test.ini'))


class SacrudTests(unittest.TestCase):

    def setUp(self):

        engine = create_engine('sqlite:///:memory:')
        DBSession = orm.scoped_session(
                                       orm.sessionmaker(extension=ZopeTransactionExtension()))

        DBSession.remove()
        DBSession.configure(bind=engine)

        session = DBSession
        self.session = session

        config = Configurator({})
        config.include('sacrud.pyramid_ext')
        settings = config.registry.settings
        settings['sacrud_models'] = (User, Profile)
        config.scan()

        # To create tables, you typically do:
        #User.metadata.create_all(engine)
        User.metadata.create_all(engine)
        Profile.metadata.create_all(engine)

        app = config.make_wsgi_app()
        self.app = app


    def tearDown(self):
        def clear_files():
            for filename in glob.glob("%s/*.html" % (PHOTO_PATH, )):
                os.remove(os.path.join(PHOTO_PATH, filename))
        clear_files()
        self.session.remove()

    def add_user(self):
        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        transaction.commit()
        user = self.session.query(User).get(1)
        return user

    def test_home_view(self):
        user = self.add_user()
        request = testing.DummyRequest()
        result = sa_home(request)

    def test_list_view(self):
        pass

    def test_add_view(self):
        pass
    
    def test_update_view(self):
        pass
    
    def test_delete_view(self):
        pass