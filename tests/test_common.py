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
import unittest

from sacrud.common import (
    get_pk,
    unjson,
    get_obj,
    pk_to_list,
    pk_list_to_dict,
    columns_by_group,
    get_flat_columns,
    get_relationship,
    get_empty_instance
)

from . import (
    User,
    Groups,
    MultiPK,
    Profile,
    BaseZopeTest,
    association_table,
    BaseSQLAlchemyTest
)


class CommonTest(unittest.TestCase):

    def test_unjson(self):
        foo = unjson(1)
        self.assertEqual(foo, 1)

    def test_unjson_json(self):
        foo = unjson('{"foo": 22}')
        self.assertEqual(foo, {'foo': 22})


class SQLAlchemyHelpersTest(object):

    def test_get_obj_with_bad_pk(self):
        self.assertEqual(None, get_obj(self.session, User, None))
        self.assertEqual(None, get_obj(self.session, User, ''))
        self.assertEqual(None, get_obj(self.session, User, {}))

    def test_get_pk(self):
        # class
        pk = get_pk(User)
        self.assertEqual('id', pk[0].name)

        # object
        user = self._add_item(User, 'Vasya', 'Pupkin', "123")
        pk = get_pk(user)
        self.assertEqual('id', pk[0].name)

    def test_table_property(self):
        user = User('Vasya', 'Pupkin', '123')
        self.assertEqual(user.foo, "I'm property")

    def test_pk_to_list(self):
        user = User('Vasya', 'Pupkin', '123')
        self.assertEqual(pk_to_list(user), ['id', None])
        self.assertEqual(pk_to_list(user, as_json=True),
                         '["id", null]')
        user.id = 100500
        self.assertEqual(pk_to_list(user), ['id', 100500])

        multipk = MultiPK(id=1, id2=1, id3=2, fk=1)
        self.assertEqual(pk_to_list(multipk),
                         ['id', 1, 'id2', 1, 'id3', 2])

        # JSON
        self.assertEqual(pk_to_list(multipk, as_json=True),
                         '["id", 1, "id2", 1, "id3", 2]')

    def test_get_relationship(self):
        foo = get_relationship(User)
        self.assertEqual(len(foo), 2)
        self.assertIn(association_table.c.user_id, foo[0].remote_side)
        self.assertIn(association_table.c.group_id, foo[0].remote_side)
        self.assertIn(Profile.__table__.c.user_id, foo[1].remote_side)

        bar = get_relationship(None)
        self.assertEqual(bar, None)

        baz = get_relationship(Groups)
        self.assertEqual(len(baz), 1)
        self.assertIn(association_table.c.user_id, foo[0].remote_side)
        self.assertIn(association_table.c.group_id, foo[0].remote_side)

    def test_pk_list_to_dict(self):
        l = ['id', 1, 'id2', 22, 'foo', 'bar']
        d = pk_list_to_dict(l)
        self.assertEqual(d, {'foo': 'bar', 'id2': 22, 'id': 1})

    def test_pk_list_to_dict2(self):
        foo = [1, 2, 3, "a", "b", {"foo": "bar"}]
        resp = pk_list_to_dict(foo)
        self.assertEqual(resp, {1: 2, 3: 'a', 'b': {'foo': 'bar'}})

        foo = [1, 2, 3, "a", "b"]
        resp = pk_list_to_dict(foo)
        self.assertEqual(resp, None)

    def test_bad_pk_list_to_dict(self):
        l = ['id', 1, 'id2', 22, 'foo']
        d = pk_list_to_dict(l)
        self.assertEqual(d, None)

    def test_columns_by_groups(self):
        c = columns_by_group(User)
        self.maxDiff = None
        table = User.__table__
        self.assertEqual(c, [('', (table.c.name, table.c.fullname,
                                   table.c.password)),
                             ('other', (table.c.sex,))]
                         )
        c = columns_by_group(Groups)
        table = Groups.__table__
        self.assertEqual(c[0][0], '')

    def test_get_flat_columns(self):
        c = get_flat_columns(User)
        table = User.__table__.c
        self.assertEqual(c, [table.name,
                             table.fullname,
                             table.password,
                             table.sex]
                         )

    def test_get_flat_columns_wo_settings(self):
        c = get_flat_columns(Groups)
        self.assertEqual(c, [])

    def test_get_empty_instance(self):
        ins = get_empty_instance(Profile)
        self.assertEqual(ins.id, None)


class ZopeTransaction(BaseZopeTest, SQLAlchemyHelpersTest):
    pass


class SQLAlchemyTransaction(BaseSQLAlchemyTest, SQLAlchemyHelpersTest):
    pass
