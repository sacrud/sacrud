# -*- coding: utf-8 -*-

import glob
import os
import unittest
from StringIO import StringIO

import transaction
from pyramid.testing import DummyRequest
from sqlalchemy import create_engine

from sacrud.action import CRUD
from sacrud.common.sa_helpers import delete_fileobj, get_pk
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
        DBSession.remove()

        def clear_files():
            files = glob.glob("%s/*.html" % PHOTO_PATH)
            files += glob.glob("%s/*.txt" % PHOTO_PATH)
            for filename in files:
                os.remove(os.path.join(PHOTO_PATH, filename))
        clear_files()


class SacrudTest(BaseSacrudTest):

    def test_get_pk(self):
        # class
        pk = get_pk(User)
        self.assertEqual('id', pk[0].name)

        # object
        user = self.user_add()
        pk = get_pk(user)
        self.assertEqual('id', pk[0].name)

    def test_list(self):
        user = User(u'Vasya', u'Pupkin', u"123")

        self.session.add(user)
        transaction.commit()

        result = CRUD(self.session, User).rows_list()
        user = self.session.query(User).get(1)

        self.assertEqual(result['pk'], 'id')
        self.assertEqual(result["prefix"], "crud")
        self.assertEqual(result["table"], User)
        self.assertEqual(result["row"], [user, ])

        self.session.delete(user)

    def test_create(self):

        request = DummyRequest().environ
        request['name'] = ["Vasya", ]
        request['fullname'] = ["Vasya Pupkin", ]
        request['password'] = ["123", ]

        CRUD(self.session, User, request=request).add()
        user = self.session.query(User).get(1)

        self.assertEqual(user.name, "Vasya")
        self.assertEqual(user.fullname, "Vasya Pupkin")
        self.assertEqual(user.password, "123")

        request = DummyRequest().environ
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["1", ]

        upload = MockCGIFieldStorage()
        upload.file = StringIO('foo')
        upload.filename = 'foo.html'
        request["photo"] = [upload, ]

        CRUD(self.session, Profile, request=request).add()

        profile = self.session.query(Profile).get(1)

        self.assertEqual(profile.phone, "213123123")
        self.assertEqual(profile.cv, "Vasya Pupkin was born in Moscow")
        self.assertEqual(profile.married, True)
        self.assertEqual(profile.salary, float(23))
        self.assertEqual(profile.user.id, 1)

        delete_fileobj(Profile, profile, "photo")

        self.session.delete(profile)
        user = self.session.query(User).get(1)
        self.session.delete(user)
        transaction.commit()

        self.assertEqual(delete_fileobj(Profile, profile, "photo"), None)

    def test_update(self):

        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        transaction.commit()

        user = self.session.query(User).get(1)
        profile = Profile(user=user, salary="25.7")

        self.session.add(profile)
        transaction.commit()

        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        transaction.commit()
        user = self.session.query(User).get(2)

        profile = self.session.query(Profile).get(1)
        request = DummyRequest().environ
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["2", ]

        upload = MockCGIFieldStorage()
        upload.file = StringIO('foo')
        upload.filename = 'foo.html'
        request["photo"] = [upload, ]

        CRUD(self.session, Profile, pk={'id': 1}, request=request).add()
        profile = self.session.query(Profile).get(1)

        self.assertEqual(profile.phone, "213123123")
        self.assertEqual(profile.cv, "Vasya Pupkin was born in Moscow")
        self.assertEqual(profile.married, True)
        self.assertEqual(profile.user.id, 2)
        self.assertEqual(profile.salary, float(23))

    def test_delete(self):

        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        transaction.commit()

        request = DummyRequest().environ
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["1", ]

        upload = MockCGIFieldStorage()
        upload.file = StringIO('foo')
        upload.filename = 'foo.html'
        request["photo"] = [upload, ]

        CRUD(self.session, Profile, request=request).add()
        CRUD(self.session, Profile, pk={'id': 1}).add()

        profile = self.session.query(Profile).get(1)
        self.assertEqual(profile, None)
        # check file also deleted
        self.assertEqual(glob.glob("%s/*.html" % (PHOTO_PATH, )), [])
