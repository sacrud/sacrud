#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Session wrap by sacrud_sessionmaker tests
"""

import unittest

import transaction
from sacrud import CRUDSession, crud_sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from . import User, Profile


class SessionMethodTest(unittest.TestCase):

    def test_session(self):
        Session = scoped_session(sessionmaker(class_=CRUDSession))
        session = Session()
        self.assertEqual(hasattr(session, 'sacrud'), True)
        self.assertEqual(hasattr(session, 'sacrud'), True)


class _ActionTest(object):

    zope = None

    def _add_item(self, table, *args, **kwargs):
        obj = table(*args, **kwargs)
        self.session.add(obj)
        if self.zope:
            transaction.commit()
        else:
            self.session.commit()
        return obj

    def test_create(self):
        user = self.session.sacrud(User)\
            .create({'name': 'Dzhirad', 'fullname': 'Kiri', 'password': 123})
        if not self.zope:
            self.session.commit()
        self.assertEqual(user.name, 'Dzhirad')
        db_user = self.session.query(User).get(user.id)
        self.assertEqual(user.id, db_user.id)

    def test_read(self):
        self._add_item(User, 'Vasya', 'Pupkin', "123")
        user = self.session.sacrud(User).read(1)
        self.assertEqual(user.name, 'Vasya')
        self.assertEqual(user.id, 1)

    def test_update(self):
        self._add_item(User, 'Vasya', 'Pupkin', "123")
        user = self.session.sacrud(User).update(1, {'name': 'Bill'})
        db_user = self.session.query(User).get(user.id)
        self.assertEqual(user.name, 'Bill')
        self.assertEqual(user.id, db_user.id)

    def test_delete(self):
        user = self._add_item(User, 'Volod', 'Khonin', "123")
        self.session.sacrud(User).delete(user.id)
        db_user = self.session.query(User).filter_by(id=user.id).all()
        self.assertEqual(db_user, [])


class ZopeSessionTest(_ActionTest, unittest.TestCase):

    zope = True

    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        self.session = crud_sessionmaker(scoped_session(
            sessionmaker(extension=ZopeTransactionExtension(),
                         expire_on_commit=False)))
        self.session.remove()
        self.session.configure(bind=engine)

        # Create tables
        User.metadata.create_all(engine)
        Profile.metadata.create_all(engine)


class SQLAlchemySessionTest(_ActionTest, unittest.TestCase):

    zope = False

    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Session = scoped_session(
            sessionmaker(class_=CRUDSession, expire_on_commit=False))
        Session.remove()
        Session.configure(bind=engine)
        self.session = Session()

        # Create tables
        User.metadata.create_all(engine)
        Profile.metadata.create_all(engine)
