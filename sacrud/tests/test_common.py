#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Test for sacrud.common
"""

import unittest
from pyramid.testing import DummyRequest
from sacrud.common import paginator


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.request = DummyRequest()

    def tearDown(self):
        pass


class PaginatorTest(BaseTest):

    def test_get_current_page(self):
        page = paginator.get_current_page(self.request)
        self.assertEqual(page, 1)
        self.request.GET['page'] = 5
        page = paginator.get_current_page(self.request)
        self.assertEqual(page, 5)
