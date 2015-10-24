import json

import pytest
from sacrud.action import CRUD
from sacrud.exceptions import CreateDublicate

from .models import User, Group, Group2User, Profile


class TestRead(object):

    def test_read(self, dbsession, init_users):
        user = CRUD(dbsession, User).read().all()
        assert len(user) == 20

    def test_read_single(self, dbsession, init_users):
        user = CRUD(dbsession, User).read(5)
        assert user.id == 5

    def test_read_by_str_id(self, dbsession, init_users):
        user = CRUD(dbsession, User).read('5')
        assert user.id == 5

    def test_read_args(self, dbsession, init_users):
        users = CRUD(dbsession, User).read(1, '2', 3, 10, 20)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    def test_read_of_tuple(self, dbsession, init_users):
        tuple_of_users = (1, 2, 3, 10, 20)
        users = CRUD(dbsession, User).read(tuple_of_users)
        assert [u.id for u in users] == list(tuple_of_users)

    def test_read_of_list(self, dbsession, init_users):
        list_of_users = [1, 2, 3, 10, 20]
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == list_of_users

    def test_read_json_of_list(self, dbsession, init_users):
        list_of_users = "[1, 2, 3, 10, 20]"
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    def test_read_tuple_of_str(self, dbsession, init_users):
        tuple_of_users = ('1', '2', 3, '10', '20')
        users = CRUD(dbsession, User).read(tuple_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    def test_read_list_of_str(self, dbsession, init_users):
        list_of_users = ['1', '2', '3', '10', '20']
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    def test_read_json_list_of_str(self, dbsession, init_users):
        list_of_users = '["1", "2", "3", "10", "20"]'
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    def test_read_by_dict_pk(self, dbsession, init_users):
        user = CRUD(dbsession, User).read({'id': 19})
        assert user.id == 19

    def test_read_json_by_dict_pk(self, dbsession, init_users):
        user = CRUD(dbsession, User).read('{"id": 19}')
        assert user.id == 19

    def test_read_list_of_dict(self, dbsession, init_users):
        list_of_users = [{'id': '1'}, {'id': '2'}, {'id': '3'},
                         {'id': 10}, {'id': 20}]
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    def test_read_json_list_of_dict(self, dbsession, init_users):
        list_of_users = '''[{"id": "1"}, {"id": "2"}, {"id": "3"},
                            {"id": 10}, {"id": 20}]'''
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    def test_read_list_of_dict_and_then_delete(self, dbsession, init_users):
        list_of_users = [{'id': '1'}, {'id': '2'}, {'id': '3'},
                         {'id': 10}, {'id': 20}]
        CRUD(dbsession, User).read(list_of_users)\
            .delete(synchronize_session=False)
        rows = [item.id for item in CRUD(dbsession, User).read().all()]
        assert 1 not in rows
        assert 2 not in rows
        assert 3 not in rows
        assert 10 not in rows
        assert 20 not in rows


class TestCreate(object):

    def test_create(self, dbsession, request_data):
        request_data['name'] = 'foo'
        group = CRUD(dbsession, Group).create(request_data)
        assert group.name == 'foo'

        db_group = dbsession.query(Group).get(group.id)
        assert group.id == db_group.id

    def test_json_create(self, dbsession, request_data):
        request_data['name'] = 'foo'
        group = CRUD(dbsession, Group).create(json.dumps(request_data))
        assert group.name == 'foo'

        db_group = dbsession.query(Group).get(group.id)
        assert group.id == db_group.id

    def test_create_twice(self, request, dbsession, transaction, request_data):
        request_data['name'] = 'foo'
        group = CRUD(dbsession, Group).create(request_data)
        assert group.name == 'foo'

        transaction.commit()

        request_data['id'] = group.id
        with pytest.raises(CreateDublicate):
            CRUD(dbsession, Group).create(request_data)

    def test_create_twice_with_update_options(
            self, dbsession, transaction, request_data):
        request_data['name'] = 'foo'
        group = CRUD(dbsession, Group).create(request_data)
        assert group.name == 'foo'

        transaction.commit()

        request_data['id'] = group.id
        request_data['name'] = 'new_foo'
        group = CRUD(dbsession, Group).create(request_data, update=True)

        transaction.commit()
        assert group.name == 'new_foo'

    def test_create_with_empty_post_request(self, dbsession, request_data):
        request_data = {}
        group = CRUD(dbsession, Group).create(request_data)
        assert group.id == 1

        db_group = dbsession.query(Group).get(group.id)
        assert group.id == db_group.id

    def test_create_json_with_empty_post_request(
            self, dbsession, request_data
    ):
        group = CRUD(dbsession, Group).create("{}")
        assert group.id == 1

        db_group = dbsession.query(Group).get(group.id)
        assert group.id == db_group.id

    # def test_create_composit_pk(
    #         self, dbsession, request_data, init_users, init_groups
    # ):
    #     CRUD(dbsession, Group2User).create({'group_id': 2, 'user_id': 1})
    #     obj = dbsession.query(Group2User).filter_by(group_id=2)\
    #         .filter_by(user_id=1).one()
    #     assert obj.group_id == 2
    #     assert obj.user_id == 1

    # def test_create_json_composit_pk(self, dbsession, request_data):
    #     CRUD(dbsession, Group2User).create('{"group_id": 2, "user_id": 1}')
    #     obj = dbsession.query(Group2User).filter_by(group_id=2)\
    #         .filter_by(user_id=1).one()
    #     assert obj.group_id == 2
    #     assert obj.user_id == 1

    # def test_create_user(self, dbsession, request_data, transaction):
    #     # Create users
    #     request = {}
    #     request_data['name'] = "Vasya"
    #     request['fullname'] = "Vasya Pupkin"
    #     request['password'] = ""  # check empty value
    #     request['groups[]'] = [u'["id", 1]', u'["id", 3]', u'["id" bad row]']
    #     request['badAttr'] = ["1", "bar"]
    #     request['badM2MAttr[]'] = ["1", "bar"]
    #     request['groups[]'] = None
    #     CRUD(dbsession, User).create(request_data)
    #     user = dbsession.query(User).get(1)
    #     assert [x.id for x in user.groups] == []
    #
    #     # Add profile
    #     request = {}
    #     request['phone'] = "213123123"
    #     request['cv'] = "Vasya Pupkin was born in Moscow"
    #     request['married'] = "true"
    #     request["salary"] = "23.0"
    #     request["user_id"] = "1"
    #
    #     CRUD(dbsession, Profile).create(request)
    #
    #     profile = dbsession.query(Profile).get(1)
    #
    #     assert profile.phone == "213123123"
    #     assert profile.cv == "Vasya Pupkin was born in Moscow"
    #     assert profile.married is True
    #     assert float(profile.salary) == float(23)
    #     assert profile.user.id == 1

    # def test_create_with_relation(self, dbsession, request_data):
    #     # Create groups (M2M example)
    #     request = {}
    #     request['name'] = 'foo'
    #     group1 = CRUD(dbsession, Group).create(request)
    #     CRUD(dbsession, Group).create(request)
    #     group3 = CRUD(dbsession, Group).create(request)
    #
    #     # Create users
    #     request = {}
    #     request['name'] = ["Vasya", ]
    #     request['fullname'] = ["Vasya Pupkin", ]
    #     request['password'] = ["", ]  # check empty value
    #     request['groups[]'] = [u'["id", 1]', u'["id", 3]', u'["id" bad row]']
    #     request['badAttr'] = ["1", "bar"]
    #     request['badM2MAttr[]'] = ["1", "bar"]
    #
    #     user = CRUD(dbsession, User).create(request)
    #     user = dbsession.query(User).get(user.id)
    #
    #     assert user.name, "Vasya")
    #     assert user.fullname, "Vasya Pupkin")
    #     assert user.password, '')
    #     assert [x.id for x in user.groups] == [group1.id, group3.id]

    def test_create_no_commit(self, dbsession, request_data, transaction):
        request_data['name'] = 'foo'
        group = CRUD(dbsession, Group).create(request_data, commit=False)
        assert group.name == 'foo'
        assert group.id is None
        transaction.commit()
        db_group = dbsession.query(Group).get(group.id)
        assert group.id == db_group.id

    # def test_create_m2m(self, dbsession, request_data):
    #     self._add_item(Group, name='foo')
    #     self._add_item(Group, name='bar')
    #     self._add_item(Group, name='baz')
    #
    #     request_data['name'] = 'foo'
    #     request_data['fullname'] = 'foo'
    #     request_data['password'] = 'foo'
    #     request_data['groups[]'] = ['["id", 1]', '["id", 2]']
    #     app = CRUD(dbsession, User).create(request_data)
    #     assert [g.id for g in app.groups] == [1, 2]
