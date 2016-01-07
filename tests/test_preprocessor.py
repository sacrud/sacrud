#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Test for sacrud.common.sa_helpers
"""
import datetime

from sacrud.action import CRUD
from sacrud.preprocessing import RequestPreprocessing

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from . import User, BaseZopeTest, TypesPreprocessor, BaseSQLAlchemyTest


class RequestPreprocessingTest(object):

    def test_preprocessor_hstore(self):
        prc = RequestPreprocessing({})
        foo = prc._check_hstore("{\"foo\":\"bar\"}")
        self.assertEqual(foo, {'foo': 'bar'})
        foo = prc._check_hstore("{'foo':\"bar\"}")
        self.assertEqual(foo, {'foo': 'bar'})
        with self.assertRaises(TypeError):
            prc._check_hstore("blablabla")

    def test_preprocessor_boolean_with_default_value(self):

        Base = declarative_base()

        class Foo(Base):
            __tablename__ = 'foo'

            id = Column(Integer, primary_key=True)
            visible = Column(Boolean, default=False)
            archive = Column(Boolean)

        prc = RequestPreprocessing({'visible': True})
        visible = prc.check_type(Foo, 'visible')
        self.assertEqual(visible, True)

        prc = RequestPreprocessing({'visible': False})
        visible = prc.check_type(Foo, 'visible')
        self.assertEqual(visible, False)

    def test_postgres_json_and_hstore_fields(self):

        from sqlalchemy.dialects.postgresql import JSON, JSONB, HSTORE

        Base = declarative_base()

        class Foo(Base):
            __tablename__ = 'foo'

            id = Column(Integer, primary_key=True)
            json = Column(JSON)
            jsonb = Column(JSONB)
            hstore = Column(HSTORE)

        prc = RequestPreprocessing({
            'json': '{"a": 1, "c": 3, "b": {"foo": true}}',
            'jsonb': '{"a": 1, "c": 3, "b": {"foo": true}}',
            'hstore': '{"a": 1, "c": 3, "b": 2}',
        })
        json = prc.check_type(Foo, 'json')
        jsonb = prc.check_type(Foo, 'jsonb')
        hstore = prc.check_type(Foo, 'hstore')
        self.assertEqual(json, {'a': 1, 'c': 3, 'b': {'foo': True}})
        self.assertEqual(jsonb, {'a': 1, 'c': 3, 'b': {'foo': True}})
        self.assertEqual(hstore, {'a': 1, 'c': 3, 'b': 2})

        prc = RequestPreprocessing({
            'json': '',
            'jsonb': '',
            'hstore': '',
        })
        json = prc.check_type(Foo, 'json')
        jsonb = prc.check_type(Foo, 'jsonb')
        hstore = prc.check_type(Foo, 'hstore')
        self.assertEqual(json, None)
        self.assertEqual(jsonb, None)
        self.assertEqual(hstore, None)

        with self.assertRaises(TypeError):
            prc._check_hstore("blablabla")

        prc = RequestPreprocessing({
            'json': [1, 2, 3],
            'jsonb': [1, 2, 3],
            'hstore': [1, 2, 3],
        })
        json = prc.check_type(Foo, 'json')
        jsonb = prc.check_type(Foo, 'jsonb')
        hstore = prc.check_type(Foo, 'hstore')
        self.assertEqual(json, [1, 2, 3])
        self.assertEqual(jsonb, [1, 2, 3])
        self.assertEqual(hstore, [1, 2, 3])

    def test_default_in_preprocessor(self):
        prc = RequestPreprocessing({'name': ''})
        foo = prc.check_type(User, 'name')
        self.assertEqual(foo, None)

    def test_polymorphycall_in_preprocessor(self):

        class Foo(User):
            __tablename__ = 'foo'
            __table_args__ = {'extend_existing': True}
            __mapper_args__ = {
                'polymorphic_identity': 'foo',
            }

            id = Column(Integer, ForeignKey('user.id'), primary_key=True)
            foo = Column(String)

        prc = RequestPreprocessing({'name': 'lalala'})
        name = prc.check_type(Foo, 'name')
        self.assertEqual(name, 'lalala')

    def test_preprocessor(self):
        request = {}
        request['date'] = "2012-12-12"
        request['datetime'] = "2012-12-12 12:12"
        request['datetimeseconds'] = "2012-12-12 12:12:12"
        request["sak"] = "Ac"
        foo = CRUD(self.session, TypesPreprocessor).create(request)

        self.assertEqual(foo.sak, bytearray(b"Ac"))
        # XXX: I feel dissonance here...
        if self.zope:
            self.assertEqual(foo.date, datetime.datetime(2012, 12, 12, 0, 0))
        else:
            self.assertEqual(foo.date, datetime.date(2012, 12, 12))

        self.assertEqual(foo.datetime,
                         datetime.datetime(2012, 12, 12, 12, 12))
        self.assertEqual(foo.datetimeseconds,
                         datetime.datetime(2012, 12, 12, 12, 12, 12))


class ZopeTransaction(BaseZopeTest, RequestPreprocessingTest):
    pass


class SQLAlchemyTransaction(BaseSQLAlchemyTest, RequestPreprocessingTest):
    pass
