# -*- coding: utf-8 -*-
"""
action.py tests
"""

import glob
import os
import unittest

import transaction
from sqlalchemy import create_engine, orm, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import LargeBinary as BYTEA
from sqlalchemy.types import (Boolean, Date, DateTime, Enum, Float, Integer,
                              String, Text, TIMESTAMP)
from zope.sqlalchemy import ZopeTransactionExtension

from sacrud.common import TableProperty
from sacrud.exttype import FileStore

Base = declarative_base()

DIRNAME = os.path.dirname(__file__)
PHOTO_PATH = os.path.join(DIRNAME)
DB_FILE = os.path.join(os.path.dirname(__file__), 'test.sqlite')
TEST_DATABASE_CONNECTION_STRING = 'sqlite:///%s' % DB_FILE


class MockCGIFieldStorage(object):
    pass


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.session2 = orm.scoped_session(orm.sessionmaker())
        self.session2.remove()
        self.session2.configure(bind=self.engine)

    def tearDown(self):

        def clear_files():
            files = glob.glob("%s/*.html" % PHOTO_PATH)
            files += glob.glob("%s/*.txt" % PHOTO_PATH)
            for filename in files:
                os.remove(os.path.join(PHOTO_PATH, filename))
        clear_files()


class BaseZopeTest(BaseTest):

    zope = True

    def _add_item(self, table, *args, **kwargs):
        obj = table(*args, **kwargs)
        self.session.add(obj)
        transaction.commit()
        return obj

    def setUp(self):
        super(BaseZopeTest, self).setUp()
        self.session = orm.scoped_session(
            orm.sessionmaker(extension=ZopeTransactionExtension(),
                             expire_on_commit=False))
        self.session.remove()
        self.session.configure(bind=self.engine)

        # Create tables
        User.metadata.create_all(self.engine)
        Profile.metadata.create_all(self.engine)


class BaseSQLAlchemyTest(BaseTest):

    zope = False

    def _add_item(self, table, *args, **kwargs):
        obj = table(*args, **kwargs)
        self.session.add(obj)
        self.session.commit()
        return obj

    def setUp(self):
        super(BaseSQLAlchemyTest, self).setUp()
        self.session = orm.scoped_session(orm.sessionmaker())
        self.session.remove()
        self.session.configure(bind=self.engine)

        # Create tables
        User.metadata.create_all(self.engine)
        Profile.metadata.create_all(self.engine)


association_table = Table('association', Base.metadata,
                          Column('group_id', Integer, ForeignKey('group.id')),
                          Column('user_id', Integer, ForeignKey('user.id'))
                          )


class Groups2User(object):

    def __init__(self, group_id, user_id):
        self.group_id = group_id
        self.user_id = user_id

mapper(Groups2User, association_table,
       primary_key=[association_table.c.group_id, association_table.c.user_id])


class Groups(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship("User", secondary=association_table)


class MultiPK(Base):

    __tablename__ = 'multipk'

    id = Column(Integer, primary_key=True)
    id2 = Column(Integer, primary_key=True)
    id3 = Column(Integer, primary_key=True)

    fk = Column('group_id', Integer, ForeignKey('group.id'))


class TypesPreprocessor(Base):
    __tablename__ = 'types_preprocessor'
    id = Column(Integer, primary_key=True)
    sak = Column(BYTEA, nullable=False)
    date = Column(Date)
    datetime = Column(DateTime)
    datetimeseconds = Column(TIMESTAMP)


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, default='')
    fullname = Column(String)
    password = Column(String, info={'verbose_name': 'user password'})
    sex = Column(Enum('male',
                      'female',
                      'alien',
                      'unknown', name="sex"))
    type = Column(String(50))

    groups = relationship("Groups", secondary=association_table)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'users',
    }

    sacrud_detail_col = [('', (name, fullname, password)),
                         ('other', (sex,))]

    @TableProperty
    def foo(self):
        return "I'm property"

    def __init__(self, name, fullname, password, sex='unknown', groups=[]):
        self.name = name
        self.fullname = fullname
        self.password = password
        self.sex = sex
        self.groups = groups


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
