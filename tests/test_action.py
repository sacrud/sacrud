#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
import json

import transaction
from sacrud.action import CRUD

import sqlalchemy

from . import (
    User,
    Groups,
    Profile,
    Groups2User,
    BaseZopeTest,
    BaseSQLAlchemyTest
)


class ReadTest(object):

    def test_read(self):
        user = CRUD(self.session, User).read().all()
        self.assertEqual(len(user), 20)

    def test_read_single(self):
        user = CRUD(self.session, User).read(5)
        self.assertEqual(user.id, 5)

    def test_read_by_str_id(self):
        user = CRUD(self.session, User).read('5')
        self.assertEqual(user.id, 5)

    def test_read_args(self):
        users = CRUD(self.session, User).read(1, '2', 3, 10, 20)
        self.assertEqual([u.id for u in users], [1, 2, 3, 10, 20])

    def test_read_of_tuple(self):
        tuple_of_users = (1, 2, 3, 10, 20)
        users = CRUD(self.session, User).read(tuple_of_users)
        self.assertEqual([u.id for u in users], list(tuple_of_users))

    def test_read_of_list(self):
        list_of_users = [1, 2, 3, 10, 20]
        users = CRUD(self.session, User).read(list_of_users)
        self.assertEqual([u.id for u in users], list_of_users)

    def test_read_json_of_list(self):
        list_of_users = "[1, 2, 3, 10, 20]"
        users = CRUD(self.session, User).read(list_of_users)
        self.assertEqual([u.id for u in users], [1, 2, 3, 10, 20])

    def test_read_tuple_of_str(self):
        tuple_of_users = ('1', '2', 3, '10', '20')
        users = CRUD(self.session, User).read(tuple_of_users)
        self.assertEqual([u.id for u in users], [1, 2, 3, 10, 20])

    def test_read_list_of_str(self):
        list_of_users = ['1', '2', '3', '10', '20']
        users = CRUD(self.session, User).read(list_of_users)
        self.assertEqual([u.id for u in users], [1, 2, 3, 10, 20])

    def test_read_json_list_of_str(self):
        list_of_users = '["1", "2", "3", "10", "20"]'
        users = CRUD(self.session, User).read(list_of_users)
        self.assertEqual([u.id for u in users], [1, 2, 3, 10, 20])

    def test_read_by_dict_pk(self):
        user = CRUD(self.session, User).read({'id': 19})
        self.assertEqual(user.one().id, 19)

    def test_read_json_by_dict_pk(self):
        user = CRUD(self.session, User).read('{"id": 19}')
        self.assertEqual(user.one().id, 19)

    def test_read_list_of_dict(self):
        list_of_users = [{'id': '1'}, {'id': '2'}, {'id': '3'},
                         {'id': 10}, {'id': 20}]
        users = CRUD(self.session, User).read(list_of_users)
        self.assertEqual([u.id for u in users], [1, 2, 3, 10, 20])

    def test_read_json_list_of_dict(self):
        list_of_users = '''[{"id": "1"}, {"id": "2"}, {"id": "3"},
                            {"id": 10}, {"id": 20}]'''
        users = CRUD(self.session, User).read(list_of_users)
        self.assertEqual([u.id for u in users], [1, 2, 3, 10, 20])

    def test_read_list_of_dict_and_then_delete(self):
        list_of_users = [{'id': '1'}, {'id': '2'}, {'id': '3'},
                         {'id': 10}, {'id': 20}]
        CRUD(self.session, User).read(list_of_users)\
            .delete(synchronize_session=False)
        rows = [item.id for item in CRUD(self.session, User).read().all()]
        self.assertNotIn(1, rows)
        self.assertNotIn(2, rows)
        self.assertNotIn(3, rows)
        self.assertNotIn(10, rows)
        self.assertNotIn(20, rows)


class CreateTest(object):

    def test_create(self):
        self.request['name'] = 'foo'
        group = CRUD(self.session, Groups).create(self.request)
        self.assertEqual(group.name, 'foo')

        db_group = self.session.query(Groups).get(group.id)
        self.assertEqual(group.id, db_group.id)

    def test_json_create(self):
        self.request['name'] = 'foo'
        group = CRUD(self.session, Groups).create(json.dumps(self.request))
        self.assertEqual(group.name, 'foo')

        db_group = self.session.query(Groups).get(group.id)
        self.assertEqual(group.id, db_group.id)

    def test_create_twice(self):
        self.request['name'] = 'foo'
        group = CRUD(self.session, Groups).create(self.request)
        self.assertEqual(group.name, 'foo')

        if self.zope:
            transaction.commit()
        else:
            self.session.commit()

        self.request['id'] = group.id
        try:
            CRUD(self.session, Groups).create(self.request)
        except Exception as e:
            if self.zope:
                from sqlalchemy.exc import IntegrityError
                transaction.abort()
                self.assertEqual(IntegrityError, type(e))
            else:
                from sqlalchemy.orm.exc import FlushError
                self.session.rollback()
                self.assertEqual(FlushError, type(e))

    def test_create_twice_with_update_options(self):
        self.request['name'] = 'foo'
        group = CRUD(self.session, Groups).create(self.request)
        self.assertEqual(group.name, 'foo')

        if self.zope:
            transaction.commit()
        else:
            self.session.commit()

        self.request['id'] = group.id
        self.request['name'] = 'new_foo'
        group = CRUD(self.session, Groups).create(self.request, update=True)

        if self.zope:
            transaction.commit()
        else:
            self.session.commit()

        self.assertEqual(group.name, 'new_foo')

    def test_create_with_empty_post_request(self):
        self.request = {}
        group = CRUD(self.session, Groups).create(self.request)
        self.assertEqual(group.id, 1)

        db_group = self.session.query(Groups).get(group.id)
        self.assertEqual(group.id, db_group.id)

    def test_create_json_with_empty_post_request(self):
        group = CRUD(self.session, Groups).create("{}")
        self.assertEqual(group.id, 1)

        db_group = self.session.query(Groups).get(group.id)
        self.assertEqual(group.id, db_group.id)

    def test_create_composit_pk(self):
        CRUD(self.session, Groups2User).create({'group_id': 2, 'user_id': 1})
        obj = self.session.query(Groups2User).filter_by(group_id=2)\
            .filter_by(user_id=1).one()
        self.assertEqual(obj.group_id, 2)
        self.assertEqual(obj.user_id, 1)

    def test_create_json_composit_pk(self):
        CRUD(self.session, Groups2User).create('{"group_id": 2, "user_id": 1}')
        obj = self.session.query(Groups2User).filter_by(group_id=2)\
            .filter_by(user_id=1).one()
        self.assertEqual(obj.group_id, 2)
        self.assertEqual(obj.user_id, 1)

    def test_create_user(self):
        # Create users
        request = {}
        request['name'] = ["Vasya", ]
        request['fullname'] = ["Vasya Pupkin", ]
        request['password'] = ["", ]  # check empty value
        request['groups[]'] = [u'["id", 1]', u'["id", 3]', u'["id" bad row]']
        request['badAttr'] = ["1", "bar"]
        request['badM2MAttr[]'] = ["1", "bar"]
        request['groups[]'] = None
        CRUD(self.session, User).create(request)
        user = self.session.query(User).get(1)
        self.assertEqual([x.id for x in user.groups], [])

        # Add profile
        request = {}
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["1", ]

        CRUD(self.session, Profile).create(request)

        profile = self.session.query(Profile).get(1)

        self.assertEqual(profile.phone, "213123123")
        self.assertEqual(profile.cv, "Vasya Pupkin was born in Moscow")
        self.assertEqual(profile.married, True)
        self.assertEqual(float(profile.salary), float(23))
        self.assertEqual(profile.user.id, 1)

    def test_create_with_relation(self):
        # Create groups (M2M example)
        request = {}
        request['name'] = 'foo'
        group1 = CRUD(self.session, Groups).create(request)
        CRUD(self.session, Groups).create(request)
        group3 = CRUD(self.session, Groups).create(request)

        # Create users
        request = {}
        request['name'] = ["Vasya", ]
        request['fullname'] = ["Vasya Pupkin", ]
        request['password'] = ["", ]  # check empty value
        request['groups[]'] = [u'["id", 1]', u'["id", 3]', u'["id" bad row]']
        request['badAttr'] = ["1", "bar"]
        request['badM2MAttr[]'] = ["1", "bar"]

        user = CRUD(self.session, User).create(request)
        user = self.session.query(User).get(user.id)

        self.assertEqual(user.name, "Vasya")
        self.assertEqual(user.fullname, "Vasya Pupkin")
        self.assertEqual(user.password, '')
        self.assertEqual([x.id for x in user.groups],
                         [group1.id, group3.id])

    def test_create_no_commit(self):
        self.request['name'] = 'foo'
        group = CRUD(self.session, Groups).create(self.request, commit=False)
        self.assertEqual(group.name, 'foo')
        self.assertEqual(group.id, None)
        if self.zope:
            transaction.commit()
        else:
            self.session.commit()
        db_group = self.session.query(Groups).get(group.id)
        self.assertEqual(group.id, db_group.id)

    def test_create_m2m(self):
        self._add_item(Groups, name='foo')
        self._add_item(Groups, name='bar')
        self._add_item(Groups, name='baz')

        self.request['name'] = 'foo'
        self.request['fullname'] = 'foo'
        self.request['password'] = 'foo'
        self.request['groups[]'] = ['["id", 1]', '["id", 2]']
        app = CRUD(self.session, User).create(self.request)
        self.assertEqual([g.id for g in app.groups], [1, 2])


class UpdateTest(object):

    def test_update_by_int_id(self):
        user = self._add_item(User, 'Vasya', 'Pupkin', "123")
        user = self.session.query(User).get(user.id)

        CRUD(self.session, User).update(user.id, data={'name': 'Petya'})
        db_user = self.session.query(User).get(user.id)
        self.assertEqual(db_user.name, 'Petya')

    def test_update_from_0_to_null(self):
        user = self._add_item(User, 'Vasya', 'Pupkin', '123')
        user = self.session.query(User).get(user.id)
        self.assertEqual(user.age, 0)

        CRUD(self.session, User).update(user.id,
                                        data={'age': sqlalchemy.sql.null()})
        db_user = self.session.query(User).get(user.id)
        self.assertEqual(db_user.age, None)

    def test_update_json_by_int_id(self):
        user = self._add_item(User, 'Vasya', 'Pupkin', "123")
        user = self.session.query(User).get(user.id)

        CRUD(self.session, User).update(user.id, data='{"name": "Petya"}')
        db_user = self.session.query(User).get(user.id)
        self.assertEqual(db_user.name, 'Petya')

    def test_update_by_str_id(self):
        user = self._add_item(User, 'Vasya', 'Pupkin', "123")
        user = self.session.query(User).get(user.id)

        CRUD(self.session, User).update(str(user.id), data={'name': 'Petya'})
        self.assertEqual(user.name, 'Petya')

    def test_update_by_composit_pk(self):
        self._add_item(Groups2User, **{'group_id': 1, 'user_id': 1})
        self._add_item(Groups2User, **{'group_id': 2, 'user_id': 1})
        self._add_item(Groups2User, **{'group_id': 3, 'user_id': 2})
        self._add_item(Groups2User, **{'group_id': 5, 'user_id': 1})

        CRUD(self.session, Groups2User)\
            .update({'group_id': 2, 'user_id': 1}, data={'group_id': '10'})
        obj = self.session.query(Groups2User).filter_by(group_id=10)\
            .filter_by(user_id=1).one()
        self.assertEqual(obj.group_id, 10)
        self.assertEqual(obj.user_id, 1)

    def test_update_json_by_composit_pk(self):
        self._add_item(Groups2User, **{'group_id': 1, 'user_id': 1})
        self._add_item(Groups2User, **{'group_id': 2, 'user_id': 1})
        self._add_item(Groups2User, **{'group_id': 3, 'user_id': 2})
        self._add_item(Groups2User, **{'group_id': 5, 'user_id': 1})

        CRUD(self.session, Groups2User)\
            .update('{"group_id": 2, "user_id": 1}', data='{"group_id": "10"}')
        obj = self.session.query(Groups2User).filter_by(group_id=10)\
            .filter_by(user_id=1).one()
        self.assertEqual(obj.group_id, 10)
        self.assertEqual(obj.user_id, 1)

    def test_update_profile(self):

        # Add user 1
        user1 = self._add_item(User, 'Vasya', 'Pupkin', "123")
        user1 = self.session.query(User).get(user1.id)
        profile = self._add_item(Profile, user=user1, salary="25.7")

        # Add user 2
        user2 = self._add_item(User, 'Vasya', 'Pupkin', "123")
        self.session.query(User).get(user2.id)

        profile = self.session.query(Profile).get(profile.id)
        request = {}
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["2", ]

        CRUD(self.session, Profile).update(pk={'id': profile.id}, data=request)
        profile = self.session.query(Profile).get(profile.id)

        self.assertEqual(profile.phone, "213123123")
        self.assertEqual(profile.cv, "Vasya Pupkin was born in Moscow")
        self.assertEqual(profile.married, True)
        self.assertEqual(profile.user.id, 2)
        self.assertEqual(float(profile.salary), float(23))

    def test_update_no_commit(self):
        user = self._add_item(User, 'Vasya', 'Pupkin', "123")
        user = self.session.query(User).get(user.id)

        CRUD(self.session2, User).update(user.id, data={'name': 'Petya'})
        db_user = self.session.query(User).get(user.id)
        self.assertEqual(db_user.name, 'Vasya')

        self.session2.commit()
        self.session.close()
        db_user = self.session.query(User).get(user.id)
        self.assertEqual(db_user.name, 'Petya')


class DeleteTest(object):

    def test_delete_by_int_id(self):
        user = self._add_item(User, 'Vasya', 'Pupkin', "123")
        user = self.session.query(User).get(user.id)

        CRUD(self.session, User).delete(user.id)
        user = self.session.query(User).filter_by(id=user.id).all()
        self.assertEqual(user, [])

    def test_delete_by_str_id(self):
        user = self._add_item(User, 'Vasya', 'Pupkin', "123")
        user = self.session.query(User).get(user.id)

        CRUD(self.session, User).delete(str(user.id))
        user = self.session.query(User).filter_by(id=user.id).all()
        self.assertEqual(user, [])

    def test_delete_by_composit_pk(self):
        self._add_item(Groups2User, **{'group_id': 3, 'user_id': 2})

        CRUD(self.session, Groups2User).delete({'group_id': 3, 'user_id': 2})
        obj = self.session.query(Groups2User).filter_by(group_id=3)\
            .filter_by(user_id=2).all()
        self.assertEqual(obj, [])

    def test_delete_json_by_composit_pk(self):
        self._add_item(Groups2User, **{'group_id': 3, 'user_id': 2})

        CRUD(self.session, Groups2User).delete('{"group_id": 3, "user_id": 2}')
        obj = self.session.query(Groups2User).filter_by(group_id=3)\
            .filter_by(user_id=2).all()
        self.assertEqual(obj, [])

    def test_delete_user(self):

        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        if self.zope:
            transaction.commit()
        else:
            self.session.commit()

        request = {}
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["1", ]

        user = CRUD(self.session, Profile).create(request)
        profile = CRUD(self.session, Profile).delete({'id': user.id})

        profile = self.session.query(Profile).get(profile['pk']['id'])
        self.assertEqual(profile, None)

    def test_delete_no_commit(self):
        user = self._add_item(User, 'Vasya', 'Pupkin', "123")
        user = self.session.query(User).get(user.id)

        CRUD(self.session2, User).delete(user.id, commit=False)
        users = self.session.query(User).filter_by(id=user.id).all()
        self.assertEqual(len(users), 1)

        self.session2.commit()
        user = self.session.query(User).filter_by(id=user.id).all()
        self.assertEqual(len(user), 0)


class ZopeTransaction(BaseZopeTest, ReadTest, CreateTest, UpdateTest,
                      DeleteTest):

    def setUp(self):
        super(ZopeTransaction, self).setUp()
        self.request = {}

        # Generator of Users
        users = [User(i, i, i) for i in range(20)]
        self.session.add_all(users)


class SQLAlchemyTransaction(BaseSQLAlchemyTest, ReadTest, CreateTest,
                            UpdateTest, DeleteTest):

    def setUp(self):
        super(SQLAlchemyTransaction, self).setUp()
        self.request = {}

        # Generator of Users
        users = [User(i, i, i) for i in range(20)]
        self.session.add_all(users)
