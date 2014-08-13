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
from sacrud.tests import BaseSacrudTest, User


class SQLAlchemyHelpersTest(BaseSacrudTest):

    def test_table_property(self):
        user = User(u'Vasya', u'Pupkin', u"123")
        self.assertEqual(user.foo, "I'm property")
