#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Models for SACRUD tests
"""
import os

import transaction
from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Boolean, Enum, Float, Integer, String, Text
from zope.sqlalchemy import ZopeTransactionExtension

from sacrud.common.sa_helpers import TableProperty
from sacrud.exttype import FileStore

Base = declarative_base()

DIRNAME = os.path.dirname(__file__)
PHOTO_PATH = os.path.join(DIRNAME)

DBSession = orm.scoped_session(
    orm.sessionmaker(extension=ZopeTransactionExtension(),
                     expire_on_commit=False))

DB_FILE = os.path.join(os.path.dirname(__file__), 'test.sqlite')
TEST_DATABASE_CONNECTION_STRING = 'sqlite:///%s' % DB_FILE


def user_add(session):
    user = User(u'Vasya', u'Pupkin', u"123")
    session.add(user)
    transaction.commit()
    user = session.query(User).get(1)
    return user


def _initTestingDB(url=TEST_DATABASE_CONNECTION_STRING):
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String, info={'verbose_name': 'user password'})
    sex = Column(Enum('male',
                      'female',
                      'alien',
                      'unknown', name="sex"))

    @TableProperty
    def foo(cls):
        return cls.name

    def __init__(self, name, fullname, password, sex='unknown'):
        self.name = name
        self.fullname = fullname
        self.password = password
        self.sex = sex


class Profile(Base):

    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship(User, backref=backref("profile", lazy="joined"))
    phone = Column(String)
    cv = Column(Text)
    married = Column(Boolean)
    salary = Column(Float)
    photo = Column(FileStore(path="/assets/photo", abspath=PHOTO_PATH))

    def __init__(self, user, phone="", cv="", married=False, salary=20.0):
        self.user = user
        self.phone = phone
        self.cv = cv
        self.married = married
        self.salary = salary
