# -*- coding: utf-8 -*-

import glob
import os
import unittest
from StringIO import StringIO

import transaction
from pyramid.testing import DummyRequest
from sqlalchemy import Column, create_engine, Integer

from sacrud.action import list as row_list
from sacrud.action import create, delete, read, update
from sacrud.common.sa_helpers import delete_fileobj, get_pk, get_relations
from sacrud.tests.test_models import DBSession, PHOTO_PATH, Profile, User


class MockCGIFieldStorage(object):
    pass


class BaseSacrudTest(unittest.TestCase):
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
        profile = self.session.query(Profile).first()
        return profile

    def setUp(self):

        engine = create_engine('sqlite:///:memory:')
        DBSession.remove()
        DBSession.configure(bind=engine)

        session = DBSession
        self.session = session

        # To create tables, you typically do:
        User.metadata.create_all(engine)
        Profile.metadata.create_all(engine)

    def tearDown(self):
        def clear_files():
            files = glob.glob("%s/*.html" % PHOTO_PATH)
            files += glob.glob("%s/*.txt" % PHOTO_PATH)
            for filename in files:
                os.remove(os.path.join(PHOTO_PATH, filename))
        clear_files()


class CustomTest(BaseSacrudTest):

    def test_relations(self):
        user = self.user_add()
        self.profile_add(user)
        user = self.session.query(User).get(1)
        profile = self.session.query(Profile).get(1)

        self.assertEqual(get_relations(user), [('profile', [profile, ])])
        self.session.delete(profile)
        self.session.delete(user)
        transaction.commit()
