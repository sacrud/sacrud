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
from sqlalchemy import Column, ForeignKey, Integer, String

from sacrud.preprocessing import RequestPreprocessing
from sacrud.tests import BaseSacrudTest, User


class RequestPreprocessingTest(BaseSacrudTest):

    def test_preprocessor_hstore(self):
        prc = RequestPreprocessing({})
        foo = prc._check_hstore("{'foo':'bar'}")
        self.assertEqual(foo, {'foo': 'bar'})
        with self.assertRaises(TypeError) as cm:
            foo = prc._check_hstore("blablabla")
        the_exception = str(cm.exception)
        self.assertEqual(the_exception,
                         'HSTORE: does\'t suppot \'blablabla\' format. Valid example: {"foo": "bar", u"baz": u"biz"}')

    def test_default_in_preprocessor(self):
        prc = RequestPreprocessing({'name': ''})
        foo = prc.check_type(User, 'name')
        self.assertEqual(foo, None)

    def test_polymorphycall_in_preprocessor(self):

        class Foo(User):
            __tablename__ = 'foo'
            __mapper_args__ = {
                'polymorphic_identity': 'foo',
            }

            id = Column(Integer, ForeignKey('user.id'), primary_key=True)
            foo = Column(String)

        prc = RequestPreprocessing({'name': 'lalala'})
        foo = prc.check_type(Foo, 'name')
        self.assertEqual(foo, 'lalala')
