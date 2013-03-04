# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import unittest
from sacrud.test_models import User, Profile
from action import get_relations
from sqlalchemy.schema import MetaData
from sacrud.action import get_pk, index


class SacrudTests(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        session = Session()
        # You probably need to create some tables and 
        # load some test data, do so here.
        self.session = session
        # To create tables, you typically do:
        #User.metadata.create_all(engine)
        User.metadata.create_all(engine)
        Profile.metadata.create_all(engine)

    def tearDown(self):
        pass

    def test_relations(self):
        user = User(u'Vasya', u'Pupkin', u"123")

        self.session.add(user)
        self.session.commit()
        profile = Profile(user=user)

        self.session.add(profile)
        self.session.commit()

        profile = self.session.query(Profile).get(1)
        self.assertEqual(get_relations(user), [('profile', [profile,])])

    def test_get_pk(self):
        pk = get_pk(User)
        self.assertEqual("id", pk)

    def test_index(self):
        user = User(u'Vasya', u'Pupkin', u"123")

        self.session.add(user)
        self.session.commit()

        result = index(self.session, User)
        self.assertEqual(result['pk'], 'id')
        self.assertEqual(result["prefix"], "crud")
        self.assertEqual(result["table"], User)
        self.assertEqual(result["row"], [user,])
