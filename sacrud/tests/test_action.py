#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
import datetime
import glob
from StringIO import StringIO

import transaction
from pyramid.testing import DummyRequest

from sacrud.action import CRUD
from sacrud.common.sa_helpers import delete_fileobj, get_pk
from sacrud.tests import (BaseSacrudTest, Groups, MockCGIFieldStorage,
                          PHOTO_PATH, Profile, TypesPreprocessor, User)


class ActionTest(BaseSacrudTest):

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

        self.assertEqual(result['pk'], (User.__table__.c['id'],))
        self.assertEqual(result["prefix"], "crud")
        self.assertEqual(result["table"], User)
        self.assertEqual(result["row"].all(), [user, ])

        self.session.delete(user)

    def test_create(self):

        # Create groups (M2M example)
        request = DummyRequest().environ
        request['name'] = 'foo'
        group1 = CRUD(self.session, Groups, request=request).add()
        group2 = CRUD(self.session, Groups, request=request).add()
        group3 = CRUD(self.session, Groups, request=request).add()

        group = self.session.query(Groups).get(2)
        self.assertEqual(group.id, group2.id)

        # Create users
        request = DummyRequest().environ
        request['name'] = ["Vasya", ]
        request['fullname'] = ["Vasya Pupkin", ]
        request['password'] = ["", ]  # check empty value
        request['groups[]'] = ["1", "3"]
        request['badAttr'] = ["1", "bar"]
        request['badM2MAttr[]'] = ["1", "bar"]

        CRUD(self.session, User, request=request).add()
        user = self.session.query(User).get(1)

        self.assertEqual(user.name, "Vasya")
        self.assertEqual(user.fullname, "Vasya Pupkin")
        self.assertEqual(user.password, None)
        self.assertEqual(map(lambda x: x.id, user.groups),
                         [group1.id, group3.id])

        # Add profile
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

    def test_create_wo_request(self):
        resp = CRUD(self.session, User).add()
        self.assertEqual(resp['table'], User)

    def test_preprocessor(self):
        # Add profile
        request = DummyRequest().environ
        request['datetime'] = "2012-12-12"
        request["sak"] = "Ac"
        foo = CRUD(self.session, TypesPreprocessor, request=request).add()
        self.assertEqual(foo.sak, "Ac")
        self.assertEqual(foo.datetime,
                         datetime.datetime(2012, 12, 12, 0, 0))

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
        CRUD(self.session, Profile, pk={'id': 1}).delete()

        profile = self.session.query(Profile).get(1)
        self.assertEqual(profile, None)
        # check file also deleted
        self.assertEqual(glob.glob("%s/*.html" % (PHOTO_PATH, )), [])
