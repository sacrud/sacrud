# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, orm
import unittest
from sacrud.tests.test_models import User, Profile, PHOTO_PATH
from sacrud.action import get_relations, delete_fileobj, read, update, delete
from sacrud.action import get_pk, index, create
from pyramid.testing import DummyRequest
from StringIO import StringIO
import glob
import os
from zope.sqlalchemy import ZopeTransactionExtension
import transaction


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

        # To create tables, you typically do:
        #User.metadata.create_all(engine)
        User.metadata.create_all(engine)
        Profile.metadata.create_all(engine)

    def tearDown(self):
        def clear_files():
            for filename in glob.glob("%s/*.html" % (PHOTO_PATH, )):
                os.remove(os.path.join(PHOTO_PATH, filename))
        clear_files()
        self.session.remove()

    def test_relations(self):
        user = User(u'Vasya', u'Pupkin', u"123")

        self.session.add(user)
        transaction.commit()

        profile = Profile(user=user)

        self.session.add(profile)
        transaction.commit()

        profile = self.session.query(Profile).get(1)
        user = self.session.query(User).get(1)

        self.assertEqual(get_relations(user), [('profile',
                                                [profile, ])])
        self.session.delete(profile)
        self.session.delete(user)
        transaction.commit()

    def test_get_pk(self):
        pk = get_pk(User)
        self.assertEqual("id", pk)

    def test_index(self):
        user = User(u'Vasya', u'Pupkin', u"123")

        self.session.add(user)
        transaction.commit()

        result = index(self.session, User)
        user = self.session.query(User).get(1)

        self.assertEqual(result['pk'], 'id')
        self.assertEqual(result["prefix"], "crud")
        self.assertEqual(result["table"], User)
        self.assertEqual(result["row"], [user, ])

        self.session.delete(user)

    def test_create(self):

        request = DummyRequest()
        request['name'] = ["Vasya", ]
        request['fullname'] = ["Vasya Pupkin", ]
        request['password'] = ["123", ]

        create(self.session, User, request)
        user = self.session.query(User).get(1)

        self.assertEqual(user.name, "Vasya")
        self.assertEqual(user.fullname, "Vasya Pupkin")
        self.assertEqual(user.password, "123")

        request = DummyRequest()
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["1", ]

        upload = MockCGIFieldStorage()
        upload.file = StringIO('foo')
        upload.filename = 'foo.html'
        request["photo"] = [upload, ]

        create(self.session, Profile, request)

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

    def test_read(self):
        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        transaction.commit()

        result = read(self.session, User, 1)
        self.assertEqual(result['obj'].id, 1)
        self.assertEqual(result['pk'], "id")
        self.assertEqual(result['prefix'], "crud")
        self.assertEqual(result['table'], User)
        self.assertEqual(result['rel'], [('profile', [])])

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
        request = DummyRequest()
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["2", ]

        upload = MockCGIFieldStorage()
        upload.file = StringIO('foo')
        upload.filename = 'foo.html'
        request["photo"] = [upload, ]

        update(self.session, Profile, 1, request)
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

        request = DummyRequest()
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["1", ]

        upload = MockCGIFieldStorage()
        upload.file = StringIO('foo')
        upload.filename = 'foo.html'
        request["photo"] = [upload, ]

        create(self.session, Profile, request)
        delete(self.session, Profile, 1)

        profile = self.session.query(Profile).get(1)
        self.assertEqual(profile, None)
        # check file also deleted
        self.assertEqual(glob.glob("%s/*.html" % (PHOTO_PATH, )), [])

